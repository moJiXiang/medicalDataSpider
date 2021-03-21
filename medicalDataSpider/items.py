# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemadapter import ItemAdapter


class KeywordItem(scrapy.Item):
    title = scrapy.Field()
    keywordList = scrapy.Field()
    source = scrapy.Field()


class ArticleItem(scrapy.Item):
    keyword = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    images = scrapy.Field()
    visits = scrapy.Field()
    likes = scrapy.Field()
    topicUrl = scrapy.Field()
    commentList = scrapy.Field()


class WendaAskItem(scrapy.Item):
    keyword = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    content = scrapy.Field()
    addtime = scrapy.Field()
    source = scrapy.Field()
    username = scrapy.Field()
    headPortrait = scrapy.Field()
    askList = scrapy.Field()
    topicUrl = scrapy.Field()


class WendaReplayItem(scrapy.Item):
    title = scrapy.Field()
    username = scrapy.Field()
    images = scrapy.Field()
    content = scrapy.Field()
    addtime = scrapy.Field()
    source = scrapy.Field()
    headPortrait = scrapy.Field()
    likes = scrapy.Field()


class HuatiItem(scrapy.Item):
    keyword = scrapy.Field()
    tagName = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    topicUrl = scrapy.Field()
    visits = scrapy.Field()
    comments = scrapy.Field()
    parent_huati = scrapy.Field()
    sub_huati = scrapy.Field()


class HuatiContentItem(scrapy.Item):
    tagName = scrapy.Field()
    keyword = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    images = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()
    visits = scrapy.Field()
    topicUrl = scrapy.Field()


class BaikeItem(scrapy.Item):
    keyword = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    content = scrapy.Field()
    likes = scrapy.Field()
    images = scrapy.Field()
    visits = scrapy.Field()
    source = scrapy.Field()


class CommentItem(scrapy.Item):
    title = scrapy.Field()
    source = scrapy.Field()
    commentList = scrapy.Field()
