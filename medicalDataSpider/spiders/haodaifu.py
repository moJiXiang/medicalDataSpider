from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, WendaAskItem


class HaodaifuSpider(Spider):
    # 爬虫名称
    name = "haodaifu_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.start_urls = [
            f'https://so.haodf.com/index/search?kw={keyword}',
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        # 根据分页数据构造url
        total = response.css("div.g-page span.ps::text").re(r'共(\d+)页')
        active = response.css("div.g-page em.active::text").get()

        next_page = ""
        if int(total[0]) > int(active):
            next_page = f'https://so.haodf.com/index/search?kw={self.keyword}&page={str(int(active) + 1)}'

        yield SplashRequest(next_page, self.parse, args={'wait': 1})

        article_urls = response.css(
            "div.sc-wz-title a.sc-wz-title-a::attr(href)").getall()

        zhuanjiaguandian_urls = []
        kanbing_urls = []
        for url in article_urls:
            if url.find("zhuanjiaguandian") >= 0:
                zhuanjiaguandian_urls.append(url)
            elif url.find("kanbing") >= 0:
                kanbing_urls.append(url)

        yield from response.follow_all(zhuanjiaguandian_urls, self.parse_article)
        yield from response.follow_all(kanbing_urls, self.parse_wenda)

    def parse_wenda(self, response):
        item = WendaAskItem()

        title = response.css("section.header-content h1::text").get()

        content = response.xpath(
            "string(.//section[@class='diseaseinfo']/div)").extract()[0].strip()

        content = content.replace("\n", "<br>")

        item["keyword"] = self.keyword
        item["title"] = title
        item["content"] = content
        yield item

    def parse_article(self, response):

        item = ArticleItem()
        item["imageList"] = []

        detail_div = response.xpath(
            './/div[@class="pb20 article_detail"]/div').get()

        content = ""
        images = []

        if detail_div:
            text = response.xpath(
                './/div[@class="pb20 article_detail"]/div/p//text()').extract()

            _text = []

            for t in text:
                _text.append(t.strip())

            content = '<br>'.join(_text)
            images = response.xpath(
                './/div[@class="pb20 article_detail"]/div//img')

        else:
            ptags = response.xpath(
                './/div[@class="pb20 article_detail"]//p')
            text = []
            for p in ptags:
                text.append(p.xpath("string()").extract()[0].strip())

            content = "<br>".join(text)

            images = response.xpath(
                './/div[@class="pb20 article_detail"]//img')

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["keyword"] = self.keyword
        item["title"] = extract_with_css("div.article_l h1.fn + p::text")
        item["author"] = extract_with_css('a.article_writer::text')
        item["content"] = content
        item["source"] = response.request.url

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        yield item
