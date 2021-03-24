
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, KeywordItem
from urllib.parse import quote, unquote


class Tm51Spider(Spider):
    # 爬虫名称
    name = "tm51_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://www.tm51.com'
        self.start_urls = [
            f'https://www.tm51.com/search.html?cate=1&keyword={keyword}'
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse_hotkeyword, args={'wait': 1})
        # for url in self.start_urls:
        #     yield SplashRequest(url, self.parse, args={'wait': 1})
    # 网页响应解析

    def parse_hotkeyword(self, response):
        # keywords = response.xpath(
        #     "//div[@class=baikeLabel]//div[@class='L-maquee']/a/label/span/text()").extract()
        keywordItem = KeywordItem()
        keywordItem["keywordList"] = []
        keywords = response.css("div.L-maquee a label span::text").getall()
        for keyword in keywords:
            keyword = keyword.strip()
            keywordItem["title"] = keyword
            keywordItem["keywordList"].append(keyword)
            keywordItem["source"] = self.index_url

        yield keywordItem

    def parse(self, response):
        current_page = response.css(
            "div.L-searchpaginbox div.m-style a.active::text").extract()[0]

        print("当前页=========>", current_page)

        urls = response.css(
            "div.postMessage ul.postInfo li p:nth-child(1) a::attr(href)").getall()

        print("urls====>", urls)

        yield from response.follow_all(urls, self.parse_article)

        # next_page = response.css(
        # "div.L-searchpaginbox div.m-style a.active + a::attr(href)").get()

        next_page = response.css(
            "div.L-searchpaginbox div.m-style a.next:nth-last-child(2)::attr(href)").extract()[0]

        next_page = unquote(next_page)

        print("next_page=====>", next_page)
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_article(self, response):

        print("parse article", response.xpath(
            "//div[@class='postDetailsContent']"))

        item = ArticleItem()
        item["imageList"] = []

        text = response.xpath(
            '//div[@class="postDetailsContent"]//text()').extract()

        _text = []

        for t in text:
            _text.append(t.strip())

        content = "<br>".join(_text)

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = extract_with_css(
            "div.postTitle::text")
        item["author"] = ""
        item["content"] = content
        item["source"] = response.request.url

        images = response.xpath(
            '//div[@class="postDetailsContent"]//img')

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        yield item
