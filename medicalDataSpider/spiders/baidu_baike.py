
import regex
import scrapy
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, request
from scrapy_splash.utils import parse_x_splash_saved_arguments_header
from medicalDataSpider.items import ArticleItem, BaikeItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    splash:go(splash.args.url)
    splash:wait(2)

    return splash:html()
end
'''


class BaiduBaikeSpider(Spider):
    # 爬虫名称
    name = "baidu_baike_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://baike.baidu.com/item/{keyword}'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, endpoint="execute", args={'lua_source': lua_script, 'wait': 1})

    def parse(self, response):
        item = BaikeItem()
        item["source"] = response.request.url
        item["keyword"] = self.keyword
        item["title"] = response.xpath(
            "//dd[@class='lemmaWgt-lemmaTitle-title']//h1//text()").extract()[0].strip()
        item["description"] = response.xpath(
            "string(//div[@class='lemma-summary'])").extract()[0].strip()
        paradivs = response.xpath(
            "//div[@class='main-content']/div[contains(@class, 'para-title') or contains(@class, 'para')]")

        text = []
        images = []
        for div in paradivs:
            t = div.xpath(
                "string()").extract()[0].strip()
            text.append(t)

            imgs = div.xpath(".//img/@src").extract()
            for img in imgs:
                if img.find("http") >= 0:
                    images.append(img)

        item["content"] = "<br>".join(text)
        item["likes"] = response.xpath(
            "//span[@class='vote-count']//text()").extract()[0]
        item["images"] = images
        item["visits"] = response.xpath(
            "//span[@id='j-lemmaStatistics-pv']//text()").extract()[0]

        yield item
