
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, KeywordItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    splash.images_enabled = false
    local num_scrolls = 5  -- 翻页数
    local scroll_delay = 1  -- 翻页等待时间
    local scroll_to = splash:jsfunc("window.scrollTo")
    local get_body_height = splash:jsfunc(
        "function() {return document.body.scrollHeight;}"
    )
    assert(splash:go(splash.args.url))
    assert(splash:wait(2))

    for _ = 1, num_scrolls do
        scroll_to(0, get_body_height())
        splash:wait(scroll_delay)
    end
    return splash:html()
end
'''


class ChaoneiSpider(Spider):
    # 爬虫名称
    name = "chaonei_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.qa_url = f'https://www.chaonei.com/qa'
        self.news_url = f'https://www.chaonei.com/news'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.qa_url, self.parse_qa_list, args={'wait': 1})
        yield SplashRequest(self.news_url, self.parse_news_list, args={'wait': 1})

    # 网页响应解析
    def parse_qa_list(self, response):
        last_a_tag_text = response.xpath(
            "//div[contains(@class, 'paging')]/a[last()]/text()")
        if last_a_tag_text == '尾页':
            next_page_url = response.xpath(
                "//div[contains(@class, 'paging')]/a[position()=last()-1]/@href")
            yield SplashRequest(response.urljoin(next_page_url), self.parse_qa_list)

        qa_list = response.xpath("//ul[contains(@class, 'lst-qa-main')]/li")

        for qa in qa_list:
            qa_url = qa.xpath(".//a[3]/@href").extract()[0]
            yield SplashRequest(response.urljoin(qa_url), self.parse_qa, args={'wait': 1}, meta={'origin_url': response.urljoin(qa_url)})

    def parse_qa(self, response):
        wendaAskItem = WendaAskItem()

        wendaAskItem["tagName"] = self.keyword

        if response.xpath("//meta[@name='keywords']"):
            wendaAskItem["keyword"] = response.xpath(
                "//meta[@name='keywords']/@content").extract()[0]
        else:
            wendaAskItem["keyword"] = ""

        wendaAskItem["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]

        wendaAskItem["title"] = response.xpath(
            "//h1[@class='audio-intro-h1']/text()").extract()[0]

        wendaAskItem["images"] = []
        wendaAskItem["content"] = response.xpath(
            "//div[@class='areat-m']/div[contains(@class, 'audio-intro-main')][1]/p/text()").extract()[0].strip()
        wendaAskItem["addtime"] = response.xpath(
            "//div[contains(@class, 'intro-ts')]/span[contains(@class, 'date')]/text()").extract()[0]
        wendaAskItem["source"] = response.meta["origin_url"]
        wendaAskItem["username"] = ""
        wendaAskItem["headPortrait"] = ""
        wendaAskItem["askList"] = []
        wendaAskItem["topicUrl"] = ""

        replyItem = WendaReplayItem()
        replyItem["title"] = wendaAskItem["title"]
        replyItem["username"] = response.xpath(
            "//div[contains(@class, 'audio-intro-l')]/a[@class='a']/span/text()").extract()[0]
        replyItem["images"] = []
        replyItem["content"] = response.xpath(
            "//div[@class='areat-m']/div[contains(@class, 'audio-intro-main')][2]/p/text()").extract()[0].strip()
        replyItem["addtime"] = wendaAskItem["addtime"]
        replyItem["source"] = response.meta["origin_url"]
        replyItem["headPortrait"] = response.xpath(
            "//div[contains(@class, 'audio-intro-l')]/a[@class='a']/img/@src").extract()[0]
        replyItem["likes"] = 0

        wendaAskItem["askList"].append(replyItem)

        otherReplys = response.xpath("//div[@class='ask-mod-item']")

        for otherReply in otherReplys:
            reply = WendaReplayItem()
            reply["title"] = wendaAskItem["title"]
            reply["username"] = otherReply.xpath(
                ".//div[@class='part-left']/a[@class='a']/@title").extract()[0]
            reply["images"] = []
            reply["content"] = otherReply.xpath(
                ".//div[contains(@class, 'audio-intro-main')]/p/text()").extract()[0].strip()
            reply["addtime"] = wendaAskItem["addtime"]
            reply["source"] = response.meta["origin_url"]
            reply["headPortrait"] = response.xpath(
                ".//div[@class='part-left']/a[@class='a']/img/@src").extract()[0]
            reply["likes"] = 0
            wendaAskItem["askList"].append(reply)

        yield wendaAskItem

    def parse_news_list(self, response):
        last_a_tag_text = response.xpath(
            "//div[contains(@class, 'paging')]/a[last()]/text()")
        if last_a_tag_text == '尾页':
            next_page_url = response.xpath(
                "//div[contains(@class, 'paging')]/a[position()=last()-1]/@href")
            yield SplashRequest(response.urljoin(next_page_url), self.parse_news_list)

        news = response.xpath(
            "//div[contains(@class, 'bk-lst-main')]/a/@href").extract()

        for news_url in news:
            yield SplashRequest(response.urljoin(news_url), self.parse_news, args={'wait': 1}, meta={'origin_url': response.urljoin(news_url)})

    def parse_news(self, response):
        article = ArticleItem()

        article["tagName"] = self.keyword

        if response.xpath(
                "//meta[@name='keywords']"):
            article["keyword"] = response.xpath(
                "//meta[@name='keywords']/@content").extract()[0]
        else:
            article["keyword"] = ""

        article["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        article["title"] = response.xpath(
            "//h1[@class='audio-intro-h1']/text()").extract()[0]
        if response.xpath("//div[@class='dr-li-item audio-intro-l']/a[@class='a']"):
            article["author"] = response.xpath(
                "//div[@class='dr-li-item audio-intro-l']/a[@class='a']/span[@class='nm']/text()").extract()[0]
        else:
            article["author"] = response.xpath(
                "//div[@class='dr-li-item audio-intro-l']/span[@class='a']/span[@class='nm']/text()").extract()[0]

        article["images"] = []
        article["visits"] = response.xpath(
            "//div[@class='intro-ts mt25']/span[contains(@class, 'shows')]/text()").extract()[0].split("阅读量：")[1]
        article["likes"] = 0
        article["topicUrl"] = ""
        article["commentList"] = []

        yield article
