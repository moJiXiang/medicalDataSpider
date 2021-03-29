from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, HuatiContentItem, HuatiItem, KeywordItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    assert(splash:go(splash.args.url))
    assert(splash:wait(2))
    return splash:html()
end
'''


class YunivfSpider(Spider):
    # 爬虫名称
    name = "yunivf_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://yunivf.com/'
        self.search_url = f'https://yunivf.com/news/news_lists.php?searchWord={keyword}'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse_keyword, args={'wait': 1})
        yield SplashRequest(self.search_url, self.parse, args={'wait': 1})

    def parse_keyword(self, response):
        tags = response.xpath(
            "//div[@class='index_label_ul']/a/text()").extract()

        keywordItem = KeywordItem()
        keywordItem["keywordList"] = []

        for keyword in tags:
            keyword = keyword.strip()
            keywordItem["title"] = ""
            keywordItem["keywordList"].append(keyword)
            keywordItem["source"] = self.index_url

        yield keywordItem

    # 网页响应解析

    def parse(self, response):
        next_page_url = response.xpath(
            "//ul[contains(@class, 'page_in_list')]/li[contains(@class, 'next_btn')]/a/@href").extract()[0]

        if next_page_url.find("/news") >= 0:
            yield SplashRequest(response.urljoin(next_page_url), self.parse, args={'wait': 1})

        articles = response.xpath("//ul[@id='successCase']/li")

        for article in articles:
            article_url = article.xpath(".//a/@href").extract()[0]
            yield SplashRequest(response.urljoin(article_url), self.parse_article, args={'wait': 1}, meta={"origin_url": response.urljoin(article_url)})

    def parse_article(self, response):
        article = ArticleItem()
        article["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        article["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        article["title"] = response.xpath(
            "//div[@class='note_detail_title']/h1/text()").extract()[0]
        article["author"] = ""

        ptags = response.xpath(
            "//div[contains(@class, 'detailinfo')]//p | //div[contains(@class, 'detailinfo')]//span")

        _text = []
        for p in ptags:
            t = p.xpath("string()").extract()[0].strip()
            t.replace('\n', '<br>')
            _text.append(t)

        article["content"] = "<br>".join(_text)
        article["source"] = response.meta["origin_url"]

        article["images"] = []
        img_tags = response.xpath("//div[contains(@class, 'detailinfo')]//img")

        for img in img_tags:
            article["images"].append(img.xpath(".//@src").extract()[0])

        article["visits"] = response.xpath(
            "//div[@class='note_detail_title']/span/dl[1]/text()").extract()[0].split("浏览：")[1]

        article["likes"] = response.xpath(
            "//div[@class='note_detail_title']/span/dl[2]/text()").extract()[0].split("点赞：")[1]

        article["topicUrl"] = 0
        article["commentList"] = []

        yield article
