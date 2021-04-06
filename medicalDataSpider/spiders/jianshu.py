from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, WendaAskItem

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


class JianshuSpider(Spider):
    # 爬虫名称
    name = "jianshu_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.start_urls = [
            f'https://www.jianshu.com/search?q={keyword}&page=1&type=note',
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint="execute", args={'lua_source': lua_script,  'wait': 1})

    # 网页响应解析
    def parse(self, response):
        active = response.xpath(
            "string(//ul[@class='pagination']/li/a[@class='active'])").extract()[0]
        next_page_text = response.css(
            "ul.pagination li:nth-last-child(1) a::text").get()
        if next_page_text == "下一页":
            next_page = f'https://www.jianshu.com/search?q={self.keyword}&page={str(int(active) + 1)}&type=note'
            yield SplashRequest(next_page, self.parse, args={'wait': 1})

        article_urls = response.xpath(
            "//ul[@class='note-list']/li/div[@class='content']/a[@class='title']/@href").extract()

        for url in article_urls:
            yield SplashRequest(response.urljoin(url), self.parse_article, endpoint="execute", args={'lua_source': lua_script}, meta={"origin_url": response.urljoin(url)})

    def parse_article(self, response):

        item = ArticleItem()
        item["images"] = []

        ptags = response.xpath(
            '//article/p')

        _text = []

        for p in ptags:
            _text.append(p.xpath("string()").extract()[0].strip())

        content = '<br>'.join(_text)

        images = response.xpath(
            '//article//img')

        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        item["tagName"] = self.keyword

        if response.xpath("//meta[@name='keywords']"):
            item["keyword"] = response.xpath(
                "//meta[@name='keywords']/@content").extract()[0]
        else:
            item["keyword"] = self.keyword

        if response.xpath("//meta[@name='description']"):
            item["description"] = response.xpath(
                "//meta[@name='description']/@content").extract()[0]
        else:
            item["description"] = ""

        item["title"] = extract_with_css("section.ouvJEz h1::text")
        item["author"] = extract_with_css('div.rEsl9f a._1OhGeD::text')
        item["content"] = content
        item["source"] = response.meta["origin_url"]

        item["visits"] = response.xpath(
            "//div[@class='rEsl9f']//div[@class='s-dsoj']/span[last()]/text()").extract()[0].split("阅读 ")[1]
        item["likes"] = extract_with_css(
            "div._1kCBjS span._1LOh_5::text").split("人点赞")[0]
        item["topicUrl"] = ""
        item["commentList"] = []

        for img in images:
            img_src = img.xpath('./@src').extract()
            if len(img_src) > 0:
                img_url = img_src[0] or ''
                item["images"].append(img_url)

        comments = response.xpath(
            "//div[@class='_2gPNSa']//div[contains(@class,'_2IUqvs _3uuww8')]")

        print("comments;   ", comments)

        for comment in comments:
            _item = {}
            _item["username"] = comment.xpath(
                ".//div[@class='_23G05g']/a").extract()[0]
            _item["content"] = comment.xpath(
                ".//div[@class='_2bDGm4']//text()").extract()[0].strip()
            _item["headPortrait"] = comment.xpath(
                ".//a[@class='_1OhGeD']/img/@src").extract()[0]
            item["commentList"].append(_item)

        yield item
