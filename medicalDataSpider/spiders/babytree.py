
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest
from medicalDataSpider.items import ArticleItem, KeywordItem, WendaAskItem, WendaReplayItem

lua_script = '''
function main(splash, args)
    assert(splash:go(splash.args.url))
    assert(splash:wait(2))
    return splash:html()
end
'''


class BabytreeSpider(Spider):
    # 爬虫名称
    name = "babytree_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'http://www.babytree.com/s.php?q={keyword}&c=ask&cid=0'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        next_page_url = response.xpath(
            "//div[@class='pg']/a[@class='nxt']/@href").extract()[0]
        if next_page_url:
            yield SplashRequest(response.urljoin(next_page_url), self.parse)

        search_list = response.xpath("//ul[@class='searchList']/li")

        for item in search_list:
            item_url = item.xpath(".//h3/a/@href").extract()[0]
            if item_url.find("article") >= 0:
                yield SplashRequest(response.urljoin(item_url), self.parse_article, args={'wait': 1}, meta={'origin_url': response.urljoin(item_url)})

        keywordItem = KeywordItem()
        keywordItem["title"] = "shiguanzhijia"
        keywordItem["keywordList"] = response.xpath(
            "//div[contains(@class, 'hotwords')]/a/text()").extract()
        keywordItem["source"] = "http://www.shiguanzhijia.cn"

        yield keywordItem

    def parse_article(self, response):
        article = ArticleItem()
        article["keyword"] = self.keyword
        article["title"] = response.xpath(
            "//div[contains(@class, 'white')]//div[@class='h hm']/h1/text()").extract()[0]
        article["author"] = "shiguanzhijia"
        article["visits"] = 0
        article_info = response.xpath(
            "string(//div[contains(@class, 'white')]//p[@class='xg1'])").extract()[0].split("|")

        for info in article_info:
            if (info.find("原作者") >= 0):
                article["author"] = info.split("原作者: ")[1]
            elif (info.find("查看") >= 0):
                article["visits"] = info.split("查看: ")[1]

        article["likes"] = 0
        article["topicUrl"] = ""
        article["commentList"] = []

        comments = response.xpath("//div[@id='comment_ul']/dl")
        if (len(comments) > 0):
            for comment in comments:
                _item = {}
                _item["username"] = comment.xpath("./dt/a/text()").extract()[0]
                _item["content"] = comment.xpath(
                    "./dd/text()").extract()[0].strip()
                article["commentList"].append(_item)

        text = []
        div_tags = response.xpath(
            "//td[@id='article_content']//div | //td[@id='article_content']//p")
        for div in div_tags:
            text.append(div.xpath("string()").extract()[0].strip())

        article["content"] = "<br>".join(text)
        article["source"] = response.meta["origin_url"]
        article["images"] = []

        imgs = response.xpath("//td[@class='article_content']//img")

        for img in imgs:
            img_url = img.xpath("./@src").extract()[0]
            article["images"].append(img_url)

        yield article
