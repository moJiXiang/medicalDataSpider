
import re
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
    root_url = 'http://www.babytree.com'

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.index_url = f'http://www.babytree.com/s.php?q={keyword}&c=ask&cid=0'

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.index_url, self.parse, args={'wait': 1})

    # 网页响应解析
    def parse(self, response):
        current_page_number = int(response.xpath(
            "//div[@class='pagejump']/span[@class='current']/text()").extract()[0])
        total_page_text = response.xpath(
            "//div[@class='pagejump']/span[@class='page-number']/text()").extract()[0]
        result = re.search(r"\d+\.?\d*", total_page_text)
        total_page = int(result.group())

        if (current_page_number < total_page):

            next_page_url = response.xpath(
                "//div[@class='pagejump']/a[position()=last()-1]/@href").extract()[0]
            yield SplashRequest(response.urljoin(next_page_url), self.parse)

        search_list = response.xpath(
            "//div[@class='search_item_area']/div[@class='search_item']")

        for item in search_list:
            item_url = item.xpath(
                ".//div[@class='search_item_tit']/a/@href").extract()[0]
            yield SplashRequest(item_url, self.parse_ask, args={'wait': 1}, meta={'origin_url': item_url})

    def parse_ask(self, response):
        wendaAskItem = WendaAskItem()
        wendaAskItem["tagName"] = self.keyword
        wendaAskItem["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        wendaAskItem["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        wendaAskItem["title"] = response.xpath(
            "//div[@class='qa-title']/h1/text()").extract()[0]
        wendaAskItem["images"] = []
        wendaAskItem["content"] = response.xpath(
            "string(//blockquote[@class='qa-text'])").extract()[0].strip()
        wendaAskItem["addtime"] = response.xpath(
            "//div[@class='qa-related']//span[@class='source']/abbr/text()").extract()[0]
        wendaAskItem["source"] = response.meta["origin_url"]

        if response.xpath("//div[@class='qa-related']/div[@class='qa-contributor']/ul/li[1]/a"):
            wendaAskItem["username"] = response.xpath(
                "//div[@class='qa-related']/div[@class='qa-contributor']/ul/li[1]/a/span/text()").extract()[0]
        else:
            wendaAskItem["username"] = response.xpath(
                "//div[@class='qa-related']/div[@class='qa-contributor']/ul/li[1]/span/text()").extract()[0]
        wendaAskItem["headPortrait"] = ""
        wendaAskItem["askList"] = []
        wendaAskItem["topicUrl"] = ""

        best_content = response.xpath("//div[@class='best-content']")

        if best_content:
            reply = WendaReplayItem()
            reply["title"] = wendaAskItem["title"]
            reply["username"] = best_content.xpath(
                ".//div[@class='qa-contributor']//span[@itemprop='accountName']/text()").extract()[0].strip()
            reply["images"] = []
            reply["content"] = best_content.xpath(
                "string(.//div[@class='answer-text'])").extract()[0].strip()
            reply["addtime"] = best_content.xpath(
                ".//li[@class='timestamp']/abbr/@title").extract()[0]
            reply["source"] = wendaAskItem["source"]
            reply["headPortrait"] = best_content.xpath(
                ".//p[@class='user-avatar']/a/img/@src").extract()[0]
            reply["likes"] = best_content.xpath(
                ".//div[@class='qa-vote']/a/em/text()").extract()[0]
            wendaAskItem["askList"].append(reply)

        reply_list = response.xpath("//ul[@class='qa-answer-list']")

        if reply_list:
            replys = reply_list.xpath("./li[@class='answer-item']")
            for reply in replys:
                wendaReply = WendaReplayItem()
                wendaReply["title"] = wendaAskItem["title"]
                wendaReply["username"] = reply.xpath(
                    ".//ul[@class='qa-meta']/li[@class='username']//span/text()").extract()[0]
                wendaReply["images"] = []
                wendaReply["content"] = reply.xpath(
                    ".//div[@class='answer-text']/text()").extract()[0].strip()
                wendaReply["addtime"] = reply.xpath(
                    ".//ul[@class='qa-meta']/li[@class='timestamp']/abbr/@title").extract()[0]
                wendaReply["source"] = wendaAskItem["source"]
                wendaReply["headPortrait"] = reply.xpath(
                    "./ul[@class='qa-meta']/li[@class='useravatar']/a/img/@src").extract()[0]
                wendaReply["likes"] = reply.xpath(
                    "./a[@class='qa-answer-list-vote']/span[@class='n']/em/text()").extract()[0]

                wendaAskItem["askList"].append(wendaReply)

        pagejump = response.xpath("//div[@class='pagejump']")
        if len(pagejump) > 0:

            pages = response.xpath("//div[@class='pagejump']/a")

            for page in pages:
                if page.xpath("./text()").extract()[0] == "下一页":
                    next_page_url = page.xpath("./@href").extract()[0]
                    yield SplashRequest(response.urljoin(next_page_url), self.parse_next_ask, args={'wait': 1}, meta={'origin_url': response.urljoin(next_page_url), 'wendaAskItem': wendaAskItem})
        else:
            yield wendaAskItem

    def parse_next_ask(self, response):
        wendaAskItem = response.meta["wendaAskItem"]
        reply_list = response.xpath("//ul[@class='qa-answer-list']")
        if reply_list:
            replys = reply_list.xpath("./li[@class='answer-item']")
            for reply in replys:
                wendaReply = WendaReplayItem()
                wendaReply["title"] = wendaAskItem["title"]
                wendaReply["username"] = reply.xpath(
                    ".//ul[@class='qa-meta']/li[@class='username']//span/text()").extract()[0]
                wendaReply["images"] = []
                wendaReply["content"] = reply.xpath(
                    ".//div[@class='answer-text']/text()").extract()[0].strip()
                wendaReply["addtime"] = reply.xpath(
                    ".//ul[@class='qa-meta']/li[@class='timestamp']/abbr/@title").extract()[0]
                wendaReply["source"] = wendaAskItem["source"]
                wendaReply["headPortrait"] = reply.xpath(
                    "./ul[@class='qa-meta']/li[@class='useravatar']/a/img/@src").extract()[0]
                wendaReply["likes"] = reply.xpath(
                    "./a[@class='qa-answer-list-vote']/span[@class='n']/em/text()").extract()[0]

                wendaAskItem["askList"].append(wendaReply)

        current_page = int(response.xpath(
            "//div[@class='pagejump']/span[@class='current']/text()").extract()[0])

        total_page_text = response.xpath(
            "//div[@class='pagejump']/span[@class='page-number']/text()").extract()[0]

        result = re.search(r"\d+\.?\d*", total_page_text)

        total_num = int(result.group())

        if current_page == total_num:
            yield wendaAskItem
