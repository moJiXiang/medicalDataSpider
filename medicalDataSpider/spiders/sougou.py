

import regex
import scrapy
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, request
from scrapy_splash.utils import parse_x_splash_saved_arguments_header
from medicalDataSpider.items import ArticleItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    splash:go(splash.args.url)
    splash:wait(2)

    return splash:html()
end
'''


class SougouSpider(Spider):
    # 爬虫名称
    name = "sougou_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://www.sogou.com/sogou?query={keyword}&ie=utf8&insite=wenwen.sogou.com&pid=sogou-wsse-a9e18cb5dd9d3ab4&rcer='

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    def parse(self, response):
        result_urls = response.xpath(
            "//div[@class='results']/div[@class='vrwrap']/h3/a/@href").extract()

        for url in result_urls:
            yield SplashRequest(response.urljoin(url),  self.parse_wenda,  endpoint="execute", args={'lua_source': lua_script, 'wait': 1}, meta={"origin_url": response.urljoin(url)})

        next_page = response.xpath("//a[@id='sogou_next']/@href").extract()[0]

        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 1})

    def parse_wenda(self, response):
        ask = WendaAskItem()
        ask["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        ask["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        ask["title"] = response.xpath(
            "//span[@class='detail-tit']/text()").extract()[0]
        ask["images"] = []
        ask["content"] = ""
        ask["addtime"] = ""
        ask["source"] = response.meta["origin_url"]
        ask["username"] = ""
        ask["headPortrait"] = ""
        ask["askList"] = []
        ask["topicUrl"] = ""

        replys = response.xpath("//div[@class='replay-section answer_item']")
        print(replys)

        if len(replys) > 0:
            for reply in replys:
                replyItem = WendaReplayItem()
                replyItem["title"] = ask["title"]
                if reply.xpath(
                        ".//a[@class='user-name']"):
                    replyItem["username"] = reply.xpath(
                        ".//a[@class='user-name']/text()").extract()[0]
                else:
                    replyItem["username"] = reply.xpath(
                        ".//span[@class='user-name']/text()").extract()[0]

                replyItem["images"] = []

                replyItem["content"] = reply.xpath(
                    "string(.//pre[contains(@class, 'answer_con')])").extract()[0].strip()

                replyItem["addtime"] = reply.xpath(
                    ".//div[@class='user-txt']/text()").extract()[0].split(" 回答")[0]
                replyItem["source"] = response.meta["origin_url"]

                if reply.xpath(
                        ".//a[@class='user-thumb']"):
                    replyItem["headPortrait"] = reply.xpath(
                        ".//a[@class='user-thumb']/img/@src").extract()[0]
                else:
                    replyItem["headPortrait"] = reply.xpath(
                        ".//div[@class='user-thumb-box']//img/@src").extract()[0]

                if reply.xpath(".//div[@class='ft-btn-box']/a"):
                    replyItem["likes"] = reply.xpath(
                        ".//div[@class='ft-btn-box']/a[1]/@data-num").extract()[0]
                else:
                    replyItem["likes"] = 0

                ask["askList"].append(replyItem)

        yield ask
