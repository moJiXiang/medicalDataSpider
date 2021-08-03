from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, WendaAskItem, WendaReplayItem


class So99Spider(Spider):
    # 爬虫名称
    name = "so99_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.kepu_url = f'https://so.99.com.cn/search.php?q={keyword}&proj=qwarc&f=_all&s=relevance'
        self.wenzhang_url = f'https://so.99.com.cn/search.php?q={keyword}&proj=oldarc&f=_all&s=relevance'
        self.wenda_url = f'https://so.99.com.cn/search.php?q={keyword}&proj=qwask&f=_all&s=relevance'

        super().__init__(**kwargs)

    def start_requests(self):
        # yield SplashRequest(self.kepu_url, self.parse_kepu, args={'wait': 1})
        # yield SplashRequest(self.wenzhang_url, self.parse, args={'wait': 1})
        yield SplashRequest(self.wenda_url, self.parse_wenda, args={'wait': 1})

    def parse_kepu(self, response):
        current_page = response.css(
            "div.pagination ul li.disabled a::text").extract()[0]

        urls = response.css("div.wz-cont dl dd h3 a::attr(href)").getall()

        yield from response.follow_all(urls, self.parse_kepu_article)

        next_page = response.css(
            "div.pagination ul li.disabled + li a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse_kepu, args={'wait': 2})

    def parse_kepu_article(self, response):
        item = ArticleItem()
        item["imageList"] = []

        ptags = response.xpath(
            '//div[@class="atcle-mid"]/div[@class="artle-cont"]/p')

        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["tagName"] = self.keyword
        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = extract_with_css(
            "div.atcle-mid div.atcle-top  h1::text")
        item["author"] = ""
        item["content"] = content
        item["source"] = response.request.url

        images = response.xpath(
            '//div[@class="atcle-mid"]/div[@class="artle-cont"]//img')

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        yield item

    def parse(self, response):
        current_page = response.css(
            "div.pagination ul li.disabled a::text").extract()[0]

        urls = response.css("dl.wrap-video dd h3 a::attr(href)").getall()

        yield from response.follow_all(urls, self.parse_article)

        next_page = response.css(
            "div.pagination ul li.disabled + li a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_article(self, response):

        item = ArticleItem()
        item["imageList"] = []

        ptags = response.xpath(
            './/div[@class="detail-box"]/div[@class="detail-cont"]/p')

        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["tagName"] = self.keyword
        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = extract_with_css(
            "div.detail-box div.detail-top  h1::text")
        item["author"] = ""
        item["content"] = content
        item["source"] = response.request.url

        images = response.xpath(
            './/div[@class="detail-box"]/div[@class="detail-cont"]//img')

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        yield item

    def parse_wenda(self, response):
        current_page = response.css(
            "div.pagination ul li.disabled a::text").extract()[0]

        urls = response.css("div.wd-cont dl dd b a::attr(href)").getall()

        yield from response.follow_all(urls, self.parse_wenda_page)

        next_page = response.css(
            "div.pagination ul li.disabled + li a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_wenda_page(self, response):
        item = WendaAskItem()

        item["tagName"] = self.keyword
        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        if response.xpath("//meta[@name='description']"):
            item["description"] = response.xpath(
                "//meta[@name='description']/@content").extract()[0]
        else:
            item["description"] = response.xpath(
                "//meta[@name='Description']/@content").extract()[0]
        item["title"] = response.css("div.dtl-top h1::text").get()
        item["images"] = []

        ptags = response.xpath("//div[@class='atcle-ms']/p")
        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        item["content"] = content
        item["addtime"] = response.css(
            "div.dtl-info span:nth-child(1)::text").get()
        item["source"] = response.request.url
        item["username"] = ""
        item["headPortrait"] = ""
        item["askList"] = []
        item["topicUrl"] = ""

        replyItem = WendaReplayItem()
        replyItem["title"] = item["title"]
        replyItem["username"] = response.css(
            "dl.dtl-ys dd b a:nth-child(1)::text").get()
        replyItem["images"] = []
        ptags = response.xpath("//div[@class='dtl-reply']/p")
        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())
        content = "<br>".join(text)
        replyItem["content"] = content
        replyItem["addtime"] = response.css(
            "div.dtl-list div.dtl-time span::text").get()

        item["askList"].append(replyItem)

        yield item
