
import regex
import scrapy
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, request
from scrapy_splash.utils import parse_x_splash_saved_arguments_header
from medicalDataSpider.items import ArticleItem, WendaAskItem, WendaReplayItem


class LamaquanSpider(Spider):
    # 爬虫名称
    name = "lamaquan_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://www.lamaquan.com/'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    def parse(self, response):

        nav_urls = response.xpath("//div[@id='bottom22']/a/@href").extract()

        for url in nav_urls:
            yield SplashRequest(response.urljoin(url), self.parse_news_list, args={'wait': 2})

    def parse_news_list(self, response):
        a_tags = response.xpath("//div[@class='tiao6']/a")

        news_urls = response.xpath(
            "//div[@class='yxli8']/ul/li/a/@href").extract()
        for url in news_urls:
            yield SplashRequest(response.urljoin(url), self.parse_news, args={'wait': 2}, meta={"origin_url": response.urljoin(url)})

        for a in a_tags:
            text = a.xpath(".//text()").extract()[0]
            if text == "下一页":
                url = a.xpath("./@href").extract()[0]
                yield SplashRequest(response.urljoin(url), self.parse_news_list, args={'wait': 2}, meta={"origin_url": response.urljoin(url)})

    def parse_news(self, response):
        article = ArticleItem()
        article["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        article["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        # article["keyword"] = response.xpath("//meta[@name='keywords']/@content").extract()[0]
        article["title"] = response.xpath(
            "//p[@class='a_title']/text()").extract()[0]
        article["author"] = response.xpath(
            "//p[@class='box_p']/span[1]/text()").extract()[0]

        article_content = response.xpath(
            "//div[@class='yxli']//td[@id='article_content']")

        if article_content:
            divs = article_content.xpath(
                "./div | ./p")
            print("divs: ", divs)
            text = []
            for d in divs:
                t = d.xpath("string()").extract()[0].strip()
                if (len(t) > 0):
                    text.append(t)
            article["content"] = "<br>".join(text)
        else:
            ptags = response.xpath(
                "//div[@class='yxli']/div/ul/ul/div | //div[@class='yxli']/div/ul/ul/p")

            if (len(ptags) > 0):

                text = []
                for p in ptags:
                    t = p.xpath("string()").extract()[0].strip()
                    if len(t) > 0:
                        text.append(t)
                article["content"] = "<br>".join(text)
            else:
                article["content"] = response.xpath(
                    "string(//div[@class='yxli']/div/ul/ul)").extract()[0]

        article["source"] = response.meta["origin_url"]
        article["images"] = []

        images = response.xpath("//div[@class='yxli']//img/@src").extract()
        if len(images) > 0:
            for img in images:
                if img.find("http") >= 0:
                    article["images"].append(img)

        article["visits"] = 0
        article["likes"] = response.xpath(
            "//td[@id='diggnum']/strong/text()").extract()[0]
        article["topicUrl"] = ""
        article["commentList"] = []

        yield article
