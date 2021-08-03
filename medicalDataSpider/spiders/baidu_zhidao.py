

import re
from scrapy.http import headers
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, KeywordItem, WendaAskItem, WendaReplayItem
from fake_useragent import UserAgent
from baiduspider import BaiduSpider
from pprint import pprint

lua_script = '''
function main(splash, args)
    splash:go(splash.args.url)
    splash:wait(2)
    return splash:html()
end
'''


# class BaiduZhidaoSpider(Spider):
#     name = "baiduzhidao_spider"
#     keyword = ""

#     def __init__(self, keyword="", **kwargs):
#         self.keyword = keyword
#         self.index = f""
#         super().__init__(**kwargs)

#     def start_requests(self):
#         spider = BaiduSpider()
#         result = spider.search_zhidao(query=self.keyword)
#         pprint(result)

#         yield None


class BaiduZhidaoSpider(Spider):
    # 爬虫名称
    name = "baidu_zhidao_spider"
    keyword = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
        "Referer": "https://www.baidu.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://zhidao.baidu.com/search?lm=0&rn=10&pn=0&fr=search&word={keyword}'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1}, meta={"pn": 1})

    def parse(self, response):
        pn = int(response.meta["pn"]) | 1
        spider = BaiduSpider()
        result = spider.search_zhidao(query=self.keyword, pn=pn)

        results = result["results"]
        for result in results:
            url = result["url"].replace("http:", "https:")
            if (url.find("zhidao.baidu") >= 0):
                yield SplashRequest(url, self.parse_zhidao, endpoint="execute", args={"lua_source": lua_script}, meta={"origin_url": url})

        if (len(results) > 0):
            next_pn = pn + 1
            yield SplashRequest(self.index_url, self.parse, meta={"pn": next_pn})

    # 网页响应解析
    # def parse(self, response):
    #     next_page_url = response.xpath(
    #         "//div[@class='pager']/a[@class='pager-next']/@href").extract()[0]
    #     if next_page_url:
    #         yield SplashRequest(response.urljoin(next_page_url), self.parse)

    #     search_list = response.xpath("//div[@class='list']/dl")

    #     for item in search_list:
    #         item_url = item.xpath(".//dt/a/@href").extract()[0]
    #         yield SplashRequest(item_url, self.parse_zhidao, args={'wait': 1}, meta={'origin_url': item_url})

    def parse_zhidao(self, response):
        ask = WendaAskItem()
        ask["tagName"] = self.keyword
        if response.xpath(
                "//meta[@name='keywords']"):
            ask["keyword"] = response.xpath(
                "//meta[@name='keywords']/@content").extract()[0]
        else:
            ask["keyword"] = ""

        if response.xpath("//meta[@name='description']"):
            ask["description"] = response.xpath(
                "//meta[@name='description']/@content").extract()[0]
        else:
            ask["description"] = ""

        ask["title"] = response.xpath(
            "//article[@id='qb-content']//span[@class='ask-title']/text()").extract()[0]
        ask["images"] = []

        image_wrap = response.xpath(
            "//article[@id='qb-content']//div[@class='q-img-wp']")
        if (len(image_wrap) > 0):
            ask["images"] = image_wrap.xpath("//img/@src").extract()

        ask["content"] = ""
        ask["addtime"] = ""
        ask["source"] = response.meta["origin_url"]
        ask["username"] = ""
        ask["headPortrait"] = ""
        ask["askList"] = []
        ask["topicUrl"] = ""

        answers = response.xpath(
            "//div[@class='bd-wrap']/div[contains(@class, 'answer')]")

        for answer in answers:
            reply = WendaReplayItem()
            reply["title"] = ask["title"]

            username = answer.xpath(
                ".//div[@class='wgt-replyer-all']//a[@class='reply-user-tohometip'][2]/span")

            if (len(username) > 0):

                reply["username"] = answer.xpath(
                    ".//div[@class='wgt-replyer-all']//a[@class='reply-user-tohometip'][2]/span/text()").extract()[0]
                reply["images"] = []

                best_text = answer.xpath(
                    ".//div[@class='line content']/div[contains(@class, 'best-text')]")

                if (len(best_text) > 0):
                    ptags = best_text.xpath(".//p")

                    text = []
                    for p in ptags:
                        text.append(p.xpath("string()").extract()[0].strip())

                    reply["content"] = "<br>".join(text)
                else:
                    reply["content"] = answer.xpath(
                        "string(.//div[@class='line content']/div[contains(@class, 'answer-text')])").extract()[0].strip()

                reply["addtime"] = answer.xpath(
                    ".//span[@class='wgt-replyer-all-time']/text()").extract()[0]

                reply["source"] = ask["source"]
                avatar_url = answer.xpath(
                    ".//div[@class='wgt-replyer-all-avatar']/@style").extract()[0]

                result = re.search(
                    r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", avatar_url)

                reply["headPortrait"] = result.group()
                good = answer.xpath(
                    ".//div[@class='wgt-eva']/span[contains(@class, 'evaluate-good-3')]")

                if good:
                    reply["likes"] = answer.xpath(
                        ".//div[@class='wgt-eva']/span[contains(@class, 'evaluate-good-3')]/@data-evaluate").extract()[0]
                else:
                    reply["likes"] = 0

                ask["askList"].append(reply)

            yield ask
