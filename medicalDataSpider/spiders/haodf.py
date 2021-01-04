from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import MedicaldataspiderItem


class ArticleSpider(Spider):
    # 爬虫名称
    name = "articles"
    # 爬虫真实的爬取url
    start_urls = [
        'https://so.haodf.com/index/search?kw=%E8%AF%95%E7%AE%A1',
    ]

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
            next_page = f'https://so.haodf.com/index/search?kw=%E8%AF%95%E7%AE%A1&page={str(int(active) + 1)}'

        yield SplashRequest(next_page, self.parse, args={'wait': 1})

        article_urls = response.css(
            "div.sc-wz-title a.sc-wz-title-a::attr(href)").getall()
        yield from response.follow_all(article_urls, self.parse_article)

    def parse_article(self, response):

        detail_div = response.xpath(
            './/div[@class="pb20 article_detail"]/div').get()
        content = ""

        if detail_div:
            content = response.xpath(
                'string(.//div[@class="pb20 article_detail"]/div)').extract()[0].strip()
        else:
            content = response.xpath(
                'string(.//div[@class="pb20 article_detail"])').extract()[0].strip()

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item = MedicaldataspiderItem()
        item["title"] = extract_with_css("div.article_l h1.fn + p::text")
        item["author"] = extract_with_css('a.article_writer::text')
        item["content"] = content

        yield item
