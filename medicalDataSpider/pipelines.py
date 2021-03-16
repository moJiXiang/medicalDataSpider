# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from medicalDataSpider.items import ArticleItem, HuatiContentItem, HuatiItem, KeywordItem, WendaAskItem
import pymongo
import requests
from itemadapter import ItemAdapter
from scrapy.item import Item
from scrapy_splash import request


class MedicaldataspiderPipeline:

    article_collection = 'articles'
    wenda_collection = "wenda"
    keyword_collection = "keyword"
    huati_collection = "huati"
    huaticontent_collection = "huati_content"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, KeywordItem):
            api = "http://spider-es-api-test1.xiaoxinfen.com/api/spider/setKeyword"

            requests.post(api, json={
                "title": item["title"],
                "keywordList": item["keywordList"],
                "source": item["source"]
            })

            self.db[self.keyword_collection].insert_one(
                ItemAdapter(item).asdict())
        elif isinstance(item, ArticleItem):
            self.db[self.article_collection].insert_one(
                ItemAdapter(item).asdict())

            api = "http://spider-es-api-test1.xiaoxinfen.com/api/spider/spiderArticle"

            requests.post(api, json={
                "article": {
                    "title": item["title"],
                    "content": item["content"],
                    "keyword": item["keyword"],
                    "description": "",
                    "imageList": item["imageList"],
                    "source": item["source"],
                    "visits": item["visits"],
                    "likes": item["likes"],
                    "topicUrl": item["topicUrl"]
                }
            })

        elif isinstance(item, WendaAskItem):
            self.db[self.wenda_collection].insert_one(
                ItemAdapter(item).asdict())

            api = "http://spider-es-api-test1.xiaoxinfen.com/api/spider/setAsk"

            askList = []

            for reply in item["askList"]:
                askList.append(dict(reply))

            requests.post(api, json={
                "keyword": item["keyword"],
                "title": item["title"],
                "description": item["description"],
                "images": item["images"],
                "content": item["content"],
                "addtime": item["addtime"],
                "source": item["source"],
                "username": item["username"],
                "headPortrait": item["headPortrait"],
                "askList": askList,
                "topicUrl": item["topicUrl"]
            })

        elif isinstance(item, HuatiItem):
            self.db[self.huati_collection].insert_one(
                ItemAdapter(item).asdict())

            api = "http://spider-es-api-test1.xiaoxinfen.com/api/spider/setHuati"

            requests.post(api, json={
                "keyword": item["keyword"],
                "tagName": item["tagName"],
                "title": item["title"],
                "content": item["content"],
                "source": item["source"],
                "topicUrl": item["topicUrl"],
                "visits": item["visits"],
                "comments": item["comments"],
                "parent_huati": item["parent_huati"],
                "sub_huati": item["sub_huati"]
            })

        elif isinstance(item, HuatiContentItem):
            self.db[self.huaticontent_collection].insert_one(
                ItemAdapter(item).asdict())
            api = "http://spider-es-api-test1.xiaoxinfen.com/api/spider/setHuatiContent"

            ask = {}

            if isinstance(item["content"], WendaAskItem):
                askList = item["content"]["askList"]
                _askList = []
                for reply in askList:
                    _askList.append(dict(reply))

                ask["keyword"] = item["content"]["keyword"]
                ask["title"] = item["content"]["title"]
                ask["description"] = item["content"]["description"]
                ask["images"] = item["content"]["images"]
                ask["content"] = item["content"]["content"]
                ask["addtime"] = item["content"]["addtime"]
                ask["source"] = item["content"]["source"]
                ask["username"] = item["content"]["username"]
                ask["headPortrait"] = item["content"]["headPortrait"]
                ask["topicUrl"] = item["content"]["topicUrl"]
                ask["askList"] = _askList

                requests.post(api, json={
                    "keyword": item["keyword"],
                    "tagName": item["tagName"],
                    "title": item["title"],
                    "content": ask,
                    "source": item["source"],
                    "likes": item["likes"],
                    "topicUrl": item["topicUrl"]
                })
            else:
                requests.post(api, json={
                    "keyword": item["keyword"],
                    "tagName": item["tagName"],
                    "title": item["title"],
                    "content": dict(item["content"]),
                    "source": item["source"],
                    "likes": item["likes"],
                    "topicUrl": item["topicUrl"]
                })

        return item
