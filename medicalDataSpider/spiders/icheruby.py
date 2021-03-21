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


class IcherubySpider(Spider):
    # 爬虫名称
    name = "icheruby_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://www.icheruby.com/tags/'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        tags = response.xpath("//span[@class='tag-item']")

        keywordItem = KeywordItem()
        keywordItem["title"] = "关键词"
        keywordItem["keywordList"] = []
        keywordItem["source"] = f'https://www.icheruby.com'

        for tag in tags:
            url = tag.xpath(".//a/@href").extract()[0]
            keyword = tag.xpath(".//a/text()").extract()[0]
            keywordItem["keywordList"].append(keyword)
            yield SplashRequest(response.urljoin(url), self.parse_topic, endpoint="execute", args={'lua_source': lua_script, 'timeout': 3600}, meta={"origin_url": response.urljoin(url), "tagName": keyword})

        yield keywordItem

    def parse_topic(self, response):
        viewport = response.xpath("//meta[@name='viewport']")

        print("viewport: ", viewport)

        huatiItem = HuatiItem()
        huatiItem["tagName"] = response.meta["tagName"]
        huatiItem["keyword"] = response.meta["tagName"]
        huatiItem["title"] = response.xpath(
            "//div[@class='tag-title']/text()").extract()[0]
        huatiItem["content"] = response.xpath(
            "//div[@class='tag-description-container']/p/text()").extract()[0]
        huatiItem["images"] = response.xpath(
            "//div[@class='tag-image']/img/@src").extract()
        huatiItem["source"] = response.meta["origin_url"]
        huatiItem["comments"] = 0

        huatiItem["visits"] = response.xpath(
            "//div[@class='tag-view-count']/span/text()").extract()[0]
        huatiItem["topicUrl"] = response.meta["origin_url"]
        huatiItem["parent_huati"] = ""
        huatiItem["sub_huati"] = []

        yield huatiItem

        huati_list = response.xpath(
            "//div[@class='tag-items']/div[@class='tag-item']")

        for huati in huati_list:
            huatiContent = HuatiContentItem()
            huatiContent["keyword"] = response.meta["tagName"]
            huatiContent["tagName"] = response.meta["tagName"]
            huatiContent["title"] = huati.xpath(
                ".//div[@class='tag-item-title']/text()").extract()[0].strip()
            huatiContent["content"] = huati.xpath(
                ".//div[@class='tag-item-desc']/text()").extract()[0].strip()
            huatiContent["source"] = response.meta["origin_url"]
            huatiContent["topicUrl"] = response.meta["origin_url"]
            huatiContent["visits"] = 0
            huatiContent["likes"] = 0

            url = huati.xpath(".//a/@href").extract()[0]

            if url.find("news") >= 0:
                yield SplashRequest(response.urljoin(url), self.parse_news, endpoint="execute", args={'tagName': response.meta["tagName"], 'lua_source': lua_script, 'timeout': 3600}, meta={"origin_url": response.urljoin(url), "tagName": response.meta["tagName"],  "topic_url": response.request.url, "huatiContent": huatiContent})

        next_page = response.xpath(
            "div[@class='page-container']/button[@class='page-button']/a")

        if next_page:
            next_page_url = next_page.xpath("./@href").extract()[0]
            yield SplashRequest(next_page_url, self.parse_topic, endpoint="execute", args={'lua_source': lua_script, 'timeout': 3600}, meta={"origin_url": next_page_url, "tagName": response.meta["tagName"]})

        # huati_list = response.xpath("//div[@class='content-container']/a")

        # for huati in huati_list:
        #     huatiContent = HuatiContentItem()
        #     huatiContent["keyword"] = response.meta["tagName"]
        #     huatiContent["tagName"] = response.meta["tagName"]
        #     huatiContent["title"] = huati.xpath(
        #         ".//div[@class='item-title']/text()").extract()[0]
        #     huatiContent["content"] = huati.xpath(
        #         ".//div[@class='item-desc']/text()").extract()[0].strip()
        #     huatiContent["source"] = response.meta["origin_url"]
        #     huatiContent["topicUrl"] = response.meta["topicUrl"]
        #     huatiContent["visits"] = response.xpath(
        #         ".//div[@class='count-number']/text()").extract()[0]

        #     url = huati.xpath("./@href").extract()

        #     if url.find("news") >= 0:
        #         yield SplashRequest(response.urljoin(url), self.parse_news, endpoint="execute", args={'tagName': response.meta["tagName"], 'lua_source': lua_script, 'timeout': 3600}, meta={"origin_url": response.urljoin(url), "topic_url": response.request.url, "huatiContent": huatiContent})
            # elif url.find("ask") >= 0:
            #     yield SplashRequest(response.urljoin(url), self.parse_ask, endpoint="execute", args={'tagName': response.meta["tagName"], 'lua_source': lua_script, 'timeout': 3600}, meta={"origin_url": response.urljoin(url), "topic_url": response.request.url,  "huatiContent": huatiContent})

    def parse_news(self, response):
        huatiContent = response.meta["huatiContent"]

        article = ArticleItem()
        article["keyword"] = response.meta["tagName"]
        article["title"] = response.xpath(
            "//div[@class='title']/text()").extract()[0]
        article["author"] = ""

        ptags = response.xpath("//div[@class='content']//p")

        _text = []
        for p in ptags:
            t = p.xpath("string()").extract()[0].strip()
            t.replace("\n", "<br>")
            _text.append(t)

        article["content"] = "<br>".join(_text)

        img_tags = response.xpath("//div[@class='content']//img")

        _images = []

        for img in img_tags:
            _images.append(img.xpath("./@src").extract()[0])

        article["images"] = _images
        article["commentList"] = []
        article["visits"] = response.xpath(
            "//div[@class='gnxx']//div[@class='onclick']/text()").extract()[0].split("已阅读")[0]
        article["likes"] = 0
        article["source"] = response.meta["origin_url"]
        article["topicUrl"] = response.meta["topic_url"]

        huatiContent["content"] = article

        yield huatiContent
