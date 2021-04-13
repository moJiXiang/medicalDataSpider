import time
from medicalDataSpider.settings import DOWNLOAD_DELAY
import regex
import scrapy
import asyncio
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, request
from medicalDataSpider.items import ArticleItem, CommentItem, HuatiContentItem, HuatiItem,  WendaAskItem, WendaReplayItem

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

    btn = splash:select('.Modal-closeButton')
    if(btn ~= nil) then
        btn:mouse_click()
    end

    for _ = 1, num_scrolls do
        scroll_to(0, get_body_height())
        splash:wait(scroll_delay)
    end
    return splash:html()
end
'''

question_lua_script = '''
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

    btn = splash:select('.Modal-closeButton')
    if(btn ~= nil) then
        btn:mouse_click()
    end

    for _ = 1, num_scrolls do
        scroll_to(0, get_body_height())
        splash:wait(scroll_delay)
    end

    comment_btns = splash:select_all('.ContentItem-actions button:nth-child(1)')

  
  	for k, btn in pairs(comment_btns) do
  		btn:mouse_click()
  	end

  	splash:set_viewport_full()
    return splash:html()
end
'''

topic_lua_script = '''
function main(splash, args)
    splash.images_enabled = false
    splash:go(splash.args.url)
    splash:wait(2)
    btn = splash:select('.Modal-closeButton')
    if(btn ~= nil) then
        btn:mouse_click()
    end
    return splash:html()
end
'''

article_lua_script = '''
function main(splash, args)
    splash.images_enabled = false
    splash:go(splash.args.url)
    splash:wait(2)
    btn = splash:select('.Modal-closeButton')
    if(btn ~= nil) then
        btn:mouse_click()
    end
    return splash:html()
end
'''


class ZhihuSpider(Spider):
    # 爬虫名称
    name = "zhihu_spider"
    keyword = ""

    custom_settings = {
        "DOWNLOAD_DELAY": 10
    }

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.start_urls = [
            f'https://www.zhihu.com/search?q={keyword}&type=topic',
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint="execute", args={'lua_source': topic_lua_script, 'timeout': 3600})

    # 话题搜索结果页面

    def parse(self, response):
        arr = []

        items = response.xpath(
            "//div[@class='List-item']")

        for item in items:
            dict = {"url": "", "title": ""}
            dict["url"] = item.xpath(
                ".//h2[@class='ContentItem-title']//a[@class='TopicLink']/@href").extract()[0]
            title = item.xpath(
                "string(.//h2[@class='ContentItem-title']//a[@class='TopicLink']//span[@class='Highlight'])").extract()[0]
            dict["title"] = title
            arr.append(dict)

        urls = []

        for _a in arr:
            # 只爬取含有关键词的话题
            urls.append(_a["url"])

        for idx, url in enumerate(urls):
            # time.sleep(5 * idx)
            yield SplashRequest(response.urljoin(url + '/hot'), self.parse_topic, endpoint="execute", args={'lua_source': topic_lua_script, 'timeout': 3600}, meta={'origin_url': url})
            yield SplashRequest(response.urljoin(url), self.parse_topic_list, endpoint="execute", args={'lua_source': lua_script, 'timeout': 3600}, meta={'origin_url': response.urljoin(url)})

    def parse_topic(self, response):
        originUrl = response.meta["origin_url"]

        huati = HuatiItem()
        huati["tagName"] = self.keyword
        huati["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        huati["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        huati["topicUrl"] = originUrl

        topicCard = response.xpath("//div[@class='TopicCard']")

        if (len(topicCard) > 0):
            huati["title"] = response.xpath(
                "//div[@class='TopicCard']//h1[@class='TopicCard-titleText']//text()").extract()[0]
            huati["content"] = response.xpath(
                "//div[@class='TopicCard']//div[@class='TopicCard-ztext']//text()").extract()[0]
        else:
            huati["title"] = response.xpath(
                "//div[@class='ContentItem TopicMetaCard-item']//div[@class='TopicMetaCard-title']//text()").extract()[0]
            huati["content"] = response.xpath(
                "string(.//div[@class='ContentItem TopicMetaCard-item']//div[@class='TopicMetaCard-description TopicMetaCard-wikiDescription'])").extract()[0]

        huati["source"] = originUrl
        visits = response.xpath(
            "string(//div[@class='NumberBoard NumberBoard--divider']/button//strong//@title)").extract()[0]
        huati["visits"] = visits
        comments = response.xpath(
            "string(//div[@class='NumberBoard NumberBoard--divider']/a//strong//@title)").extract()[0]
        huati["comments"] = comments
        if response.xpath("//div[@class='TopicRelativeBoard-item'][1]//span[@class='Tag-content']"):
            huati["parent_huati"] = response.xpath(
                "//div[@class='TopicRelativeBoard-item'][1]//span[@class='Tag-content']//text()").extract()[0]
        else:
            huati["parent_huati"] = []

        if response.xpath("// div[@class='TopicRelativeBoard-item'][2]"):
            huati["sub_huati"] = response.xpath(
                "//div[@class='TopicRelativeBoard-item'][2]//a[contains(@class, 'TopicLink')]//span[@class='Tag-content']//text()").extract()
        else:
            huati["sub_huati"] = []

        yield huati

    def parse_topic_list(self, response):
        originUrl = response.meta["origin_url"]

        topic_list = response.xpath("//div[@class='List-item TopicFeedItem']")

        for idx, topic in enumerate(topic_list):
            # time.sleep(idx * 5)
            url = topic.xpath(
                ".//h2[@class='ContentItem-title']//a/@href").extract()[0]

            huatiContent = HuatiContentItem()
            huatiContent["tagName"] = self.keyword
            huatiContent["keyword"] = response.xpath(
                "//meta[@name='keywords']/@content").extract()[0]
            huatiContent["title"] = topic.xpath(
                "string(.//h2[@class='ContentItem-title']//a)").extract()[0]
            huatiContent["content"] = topic.xpath(
                "string(.//div[contains(@class, 'RichContent')]//span)").extract()[0].strip()

            huatiContent["source"] = originUrl
            huatiContent["topicUrl"] = originUrl
            huatiContent["likes"] = topic.xpath(
                ".//div[@class='ContentItem-actions']//button[contains(@class, 'VoteButton--up')]/@aria-label").extract()[0].split("赞同")[1].strip()

            comment_text = topic.xpath(
                ".//div[@class='ContentItem-actions']/button[contains(@class, 'ContentItem-action')][1]//text()").extract()[0]

            if comment_text.find("条评论") >= 0:
                huatiContent["comments"] = comment_text.split(" 条评论")[0]
            else:
                huatiContent["comments"] = 0

            huatiContent["visits"] = 0

            if url.find("question") >= 0:
                questionurl, _ = url.split("/answer")
                yield SplashRequest(response.urljoin(questionurl), self.parse_question_page, endpoint="execute", args={'lua_source': lua_script, 'timeout': 3600}, meta={'topic_url': originUrl, "origin_url": response.urljoin(questionurl), "huatiContent": huatiContent})
            else:
                yield SplashRequest(response.urljoin(url), self.parse_article_page, endpoint="execute", args={'lua_source': lua_script, 'timeout': 3600}, meta={'topic_url': originUrl, "origin_url": response.urljoin(url), "huatiContent": huatiContent})

    def parse_question_page(self, response):
        huatiContent = response.meta["huatiContent"]
        wenda = WendaAskItem()
        wenda["tagName"] = self.keyword
        wenda["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        wenda["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        wenda["title"] = response.xpath(
            "//div[@class='QuestionHeader']//h1[@class='QuestionHeader-title']/text()").extract()[0]

        if response.xpath(
                "//div[@class='QuestionHeader']//div[contains(@class, 'QuestionRichText')]//p"):
            wenda["content"] = response.xpath(
                "string(//div[@class='QuestionHeader']//div[contains(@class, 'QuestionRichText')]//p)").extract()[0]
        else:
            wenda["content"] = ""

        wenda["description"] = ""
        wenda["images"] = []
        wenda["source"] = response.meta["origin_url"]
        wenda["username"] = ""
        wenda["headPortrait"] = ""
        wenda["askList"] = []
        wenda["addtime"] = ""
        wenda["topicUrl"] = response.meta["topic_url"]

        visits = response.xpath(
            "//div[@class='QuestionFollowStatus']//strong[@class='NumberBoard-itemValue']//@title").extract()[0]

        replys = response.xpath("//div[@class='List-item']")

        for reply in replys:
            replyItem = WendaReplayItem()
            replyItem["title"] = wenda["title"]

            common_username = reply.xpath(
                ".//div[@class='AuthorInfo-content']//a[@class='UserLink-link']")

            if common_username:
                replyItem["username"] = reply.xpath(
                    ".//div[@class='AuthorInfo-content']//span//text()").extract()[0]
            else:
                userLink = reply.xpath(
                    ".//div[@class='AuthorInfo-content']//a[@class='UserLink-link']")

                if userLink:
                    replyItem["username"] = reply.xpath(
                        ".//div[@class='AuthorInfo-content']//a[@class='UserLink-link']//text()").extract()[0]
                else:
                    replyItem["username"] = reply.xpath(
                        ".//div[@class='AuthorInfo-contet']//span//text()").extract()[0]

            replyItem["images"] = []

            text = []
            ptags = reply.xpath(
                ".//div[contains(@class, 'RichContent')]//span[contains(@class, 'RichText')]/p")
            for p in ptags:
                text.append(p.xpath("string()").extract()[0])

            replyItem["content"] = '<br>'.join(text)
            _, addtime = reply.xpath(
                ".//div[@class='ContentItem-time']//span/@data-tooltip").extract()[0].split("发布于 ")
            replyItem["addtime"] = addtime
            replyItem["source"] = response.meta["origin_url"]
            replyItem["headPortrait"] = reply.xpath(
                ".//span[@class='UserLink AuthorInfo-avatarWrapper']//img/@src").extract()[0]
            _, likes = reply.xpath(
                ".//div[contains(@class, 'ContentItem-actions')]/span/button[contains(@class, 'VoteButton--up')]/@aria-label").extract()[0].split("赞同 ")
            replyItem["likes"] = likes
            wenda["askList"].append(replyItem)

        huatiContent["content"] = wenda
        huatiContent["visits"] = visits

        yield huatiContent

    def parse_article_page(self, response):
        huatiContent = response.meta["huatiContent"]

        post = response.xpath("//article[@class='Post-Main Post-NormalMain']")
        if (len(post) == 0):
            return None

        article = ArticleItem()
        article["tagName"] = self.keyword
        article["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        article["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        article["title"] = response.xpath(
            "//article[@class='Post-Main Post-NormalMain']/header[@class='Post-Header']/h1/text()").extract()[0]
        article["author"] = response.xpath(
            "//div[@class='AuthorInfo-head']//a[@class='UserLink-link']/text()").extract()[0]

        ptags = response.xpath("//div[@class='Post-RichTextContainer']/div/p")
        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        article["content"] = "<br>".join(text)
        article["images"] = []
        article["commentList"] = []

        images = response.xpath(
            "//div[@class='Post-RichTextContainer']//img")
        for img in images:
            img_url = img.xpath("./@src").extract()[0]
            if img_url.find("http") == 0:
                article["images"].append(img_url)

        article["visits"] = 0
        likesText = response.xpath(
            "//div[@class='ContentItem-actions']/span/button[contains(@class, 'VoteButton--up')]/text()").extract()[0].strip()
        article["likes"] = likesText.split("赞同")[1]
        article["source"] = response.meta["origin_url"]
        article["topicUrl"] = response.meta["topic_url"]

        comments = response.xpath("//div[@class='CommentItemV2']")

        if (len(comments) > 0):
            for comment in comments:
                _item = {}
                if comment.xpath(".//span[@class='UserLink']/a"):
                    _item["username"] = comment.xpath(
                        ".//span[@class='UserLink']/a/text()").extract()[0]
                else:
                    _item["username"] = "知乎用户"
                _item["content"] = comment.xpath(
                    "string(.//div[@class='CommentItemV2-metaSibling'])").extract()[0]
                _item["headPortrait"] = comment.xpath(
                    ".//span[@class='UserLink CommentItemV2-avatar']//img/@src").extract()[0]

                article["commentList"].append(_item)

        huatiContent["content"] = article

        yield huatiContent
