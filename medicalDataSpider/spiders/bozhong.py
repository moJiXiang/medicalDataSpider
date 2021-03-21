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


class BozhongSpider(Spider):
    # 爬虫名称
    name = "bozhong_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'https://www.bozhong.com/search?s=11&q={keyword}',

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        active = response.xpath(
            "string(//article[@class='search-pagination']/a[@class='search-pagination__item active'])").extract()[0]
        next_page = response.xpath(
            "//article[@class='search-pagination']/a[@class='search-pagination__item next']")
        if next_page:
            next_page = f'https://www.bozhong.com/search?s=11&q={self.keyword}&page={str(int(active) + 1)}'
            yield SplashRequest(next_page, self.parse, args={'wait': 1})

        article_urls = response.xpath(
            "//ul[@class='search-list']/li/a[@class='thread-title']/@href").extract()

        for url in article_urls:
            yield SplashRequest(response.urljoin(url), self.parse_wenda, endpoint="execute", args={'lua_source': lua_script}, meta={"origin_url": response.urljoin(url)})

    def parse_wenda(self, response):

        item = WendaAskItem()
        item["keyword"] = self.keyword
        item["title"] = response.xpath(
            "//h1[@class='ts-title']/text()").extract()[0]
        item["description"] = ""
        item["images"] = []

        content_table = response.xpath(
            "//div[@class='theme_box post_list']//div[@class='topic_main list_box']//div[@class='fsz_main']")

        if content_table:
            item["content"] = response.xpath(
                "//div[@class='theme_box post_list']//div[@class='topic_main list_box']//div[@class='fsz_main']/table//td/text()").extract()[0].strip()
        else:
            item["content"] = ""

        addtime_span_tag = response.xpath(
            "//div[@class='theme_box post_list']//div[@class='auth_info_main']/em/span")
        if addtime_span_tag:
            item["addtime"] = addtime_span_tag.xpath("./@title").extract()[0]
        else:
            item["addtime"] = response.xpath(
                "//div[@class='theme_box post_list']//div[@class='auth_info_main']/em").extract()[0].strip().split("发表于 ")[1]
        item["source"] = response.meta["origin_url"]
        item["username"] = response.xpath(
            "//div[@class='theme_box post_list']//div[@class='auth_info_bar']//a/text()").extract()[0]
        item["headPortrait"] = response.xpath(
            "//div[@class='theme_box post_list']/div[@class='auth_info']//div[@class='avatar']/img/@src").extract()[0]
        item["askList"] = []
        item["topicUrl"] = ""

        replys = response.xpath(
            "//div[@class='list_box theme_reply']//div[contains(@class, 'post_list')]")

        for reply in replys:
            replyItem = WendaReplayItem()
            replyItem["title"] = item["title"]
            username_tag = reply.xpath(
                ".//div[@class='user_name']/a")
            if username_tag:
                replyItem["username"] = reply.xpath(
                    ".//div[@class='user_name']/a/text()").extract()[0]
            else:
                continue
            replyItem["images"] = []

            content_table = reply.xpath(".//div[@class='fsz_main']")
            if content_table:
                replyItem["content"] = reply.xpath(
                    ".//div[@class='fsz_main']/table//td/text()").extract()[0].strip()
            else:
                replyItem["content"] = ""
            replyItem['addtime'] = reply.xpath(
                ".//div[@class='auth_info_main']/em/text()").extract()[0].split("发表于 ")[1]
            replyItem["source"] = item["source"]
            avatar_tag = reply.xpath(
                ".//div[@class='avatar']/img")
            if avatar_tag:
                replyItem["headPortrait"] = reply.xpath(
                    ".//div[@class='avatar']/img/@src").extract()[0]
            else:
                replyItem["headPortrait"] = ""
            replyItem["likes"] = 0

            item["askList"].append(replyItem)

        yield item

        tag_box = response.xpath(
            "//div[@class='mod_s tag_box']/div[@class='mod_con']/a/text()")

        for keyword in tag_box:
            keyword = keyword.strip()
            item = KeywordItem()
            item["title"] = keyword
            item["keywordList"] = []
            item["keywordList"].append(keyword)
            item["source"] = self.index_url
            yield item
