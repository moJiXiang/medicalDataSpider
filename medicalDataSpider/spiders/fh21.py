
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem


class Fh21Spider(Spider):
    # 爬虫名称
    name = "fh21_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.start_urls = [
            f'http://so.fh21.com.cn/?kw={keyword}&type=article',
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 1})
    # 网页响应解析

    def parse(self, response):
        current_page = response.css(
            "div.pageStyle p span.current::text").extract()[0]

        urls = response.css("div.repository a::attr(href)").getall()

        pc_urls = []
        for url in urls:
            if url.find("m.fh21") < 0:
                pc_urls.append(url)

        yield from response.follow_all(pc_urls, self.parse_article)

        next_page = response.css(
            "div.pageStyle p span.current + a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_article(self, response):

        item = ArticleItem()
        item["tagName"] = self.keyword
        item["images"] = []

        ptags = response.xpath(
            './/div[@class="main_content"]//div[@class="detail"]/ul[@class="detailc"]//p')

        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = extract_with_css(
            "div.detail > ul.detaila::text")
        item["content"] = content
        item["source"] = response.request.url

        info = response.xpath(
            "//div[@class='detail']/ul[@class='detailb']/ul[1]/text()").extract()[0]
        [_, author, visits] = info.split("\xa0\xa0\xa0\xa0")

        item["author"] = author.split("来源：")[1]
        item["visits"] = visits.split("浏览数：")[1]
        item["likes"] = 0
        item["topicUrl"] = ""
        item["commentList"] = []

        yield item
