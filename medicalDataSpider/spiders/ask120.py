

import re
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, KeywordItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    assert(splash:go(splash.args.url))
    assert(splash:wait(2))
    return splash:html()
end
'''


class Ask120Spider(Spider):
    # 爬虫名称
    name = "ask120_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'http://so.120ask.com/?nsid=5&kw={keyword}'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        next_page = response.xpath(
            "//div[@class='p_pagediv']/a[last()]/@href").extract()[0]

        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse)

        search_list = response.xpath(
            "//ul[@id='datalist']/li")

        for item in search_list:
            item_url = item.xpath(
                ".//h3/a/@href").extract()[0]
            yield SplashRequest(item_url, self.parse_ask, args={'wait': 1}, meta={'origin_url': item_url})

    def parse_ask(self, response):
        wendaAskItem = WendaAskItem()
        wendaAskItem["tagName"] = self.keyword
        wendaAskItem["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        wendaAskItem["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        wendaAskItem["title"] = response.xpath(
            "//h1[@id='d_askH1']/text()").extract()[0]
        wendaAskItem["images"] = []
        wendaAskItem["content"] = response.xpath(
            "string(//div[@class='b_askcont']/p[@class='crazy_new'])").extract()[0].strip()
        wendaAskItem["addtime"] = response.xpath(
            "//div[@class='b_askab1']//span[2]/text()").extract()[0]
        wendaAskItem["source"] = response.meta["origin_url"]

        if response.xpath(
                "//var[@class='ask_Author']"):
            wendaAskItem["username"] = response.xpath(
                "//var[@class='ask_Author']/text()").extract()[0]
        else:
            wendaAskItem["username"] = "匿名会员"
        wendaAskItem["headPortrait"] = ""
        wendaAskItem["askList"] = []
        wendaAskItem["topicUrl"] = ""

        reply_list = response.xpath(
            "//div[contains(@class, 'b_answerbox')]/div[@class='b_answerli']")

        if reply_list:
            for reply in reply_list:
                wendaReply = WendaReplayItem()
                wendaReply["title"] = wendaAskItem["title"]
                if(reply.xpath(
                        ".//div[contains(@class, 'b_answertop')]//span[@class='b_sp1']/a")):
                    wendaReply["username"] = reply.xpath(
                        ".//div[contains(@class, 'b_answertop')]//span[@class='b_sp1']/a/text()").extract()[0]
                else:
                    wendaReply["username"] = reply.xpath(
                        ".//div[contains(@class, 'b_answertop')]//span[@class='b_sp1']/var/text()").extract()[0]
                wendaReply["images"] = []
                if(reply.xpath(
                        ".//div[contains(@class, 'b_answercont')]//div[@class='crazy_new']/p")):
                    wendaReply["content"] = reply.xpath(
                        ".//div[contains(@class, 'b_answercont')]//div[@class='crazy_new']/p/text()").extract()[0].strip()
                else:
                    wendaReply["content"] = ""

                if reply.xpath(".//div[contains(@class, 'b_answercont')]//span[@class='b_anscont_time']"):
                    wendaReply["addtime"] = reply.xpath(
                        ".//div[contains(@class, 'b_answercont')]//span[@class='b_anscont_time']/text()").extract()[0].strip()
                else:
                    wendaReply["addtime"] = ""

                wendaReply["source"] = wendaAskItem["source"]
                if reply.xpath(
                        "./div[contains(@class, 'b_answertop')]/a[@class='b_docface']"):
                    wendaReply["headPortrait"] = reply.xpath(
                        "./div[contains(@class, 'b_answertop')]/a[@class='b_docface']/img/@src").extract()[0]
                else:
                    wendaReply["headPortrait"] = reply.xpath(
                        "./div[contains(@class, 'b_answertop')]/var[@class='b_docface']/img/@src").extract()[0]
                info = reply.xpath(
                    "string(./div[contains(@class, 'b_answertop')]/div[@class='b_answertl']/span[@class='b_sp2'][2])").extract()[0]

                if info:

                    result = re.search(r"\d+\.?\d*", info)
                    if result.group():
                        wendaReply["likes"] = result.group()
                    else:
                        wendaReply["likes"] = 0
                else:
                    wendaReply["likes"] = 0

                wendaAskItem["askList"].append(wendaReply)

        yield wendaAskItem
