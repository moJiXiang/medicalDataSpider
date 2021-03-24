import regex
import scrapy
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, request
from scrapy_splash.utils import parse_x_splash_saved_arguments_header
from medicalDataSpider.items import ArticleItem, WendaAskItem, WendaReplayItem


class So39Spider(Spider):
    # 爬虫名称
    name = "so39_spider"
    keyword = ""

    def __init__(self, keyword="", **kwargs):
        self.keyword = keyword
        self.wenda_url = f'http://so.39.net/search/wd?words={keyword}'
        self.start_urls = [
            f'http://so.39.net/search/jb?words={keyword}',
        ]

        super().__init__(**kwargs)

    def start_requests(self):
        yield SplashRequest(self.wenda_url, self.parse_wenda, args={'wait': 1})
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 1})

    def parse(self, response):
        current_page = response.css(
            "div.con_page span::text").get()

        urls = response.css("ol.con_list li dl dt a::attr(href)").getall()

        yield from response.follow_all(urls, self.parse_article)

        next_page = response.css(
            "div.con_page span + a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_wenda(self, response):
        urls = response.css("ol.con_list li dl dt a::attr(href)").getall()

        yield from response.follow_all(urls, self.parse_wenda_page)

        next_page = response.css(
            "div.con_page span + a::attr(href)").get()
        if next_page:
            yield SplashRequest(response.urljoin(next_page), self.parse, args={'wait': 2})

    def parse_wenda_page(self, response):
        item = WendaAskItem()
        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = response.css(
            "div.ask_cont p.ask_tit::text").get().strip()
        item["images"] = []
        item["content"] = response.css(
            "div.ask_cont div.ask_hid p.txt_ms::text").get().strip()
        item["addtime"] = response.css(
            "div.ask_cont p.txt_nametime span:nth-child(2)::text").get().strip()
        item["source"] = response.request.url
        item["username"] = response.css(
            "div.ask_cont p.txt_nametime span:nth-child(1)::text").get().strip()
        item["headPortrait"] = ""
        item["askList"] = []
        item["topicUrl"] = ""

        replys = response.css("div.selected div.sele_all")

        for reply in replys:
            replyItem = WendaReplayItem()
            replyItem["title"] = item["title"]
            replyItem["username"] = reply.css(
                "div.doc_txt p.doc_xinx span:nth-child(1)::text").get().strip()
            replyItem["likes"] = 0
            replyItem["headPortrait"] = reply.css(
                "div.doc_img a img::attr(src)").get()
            replyItem["images"] = []
            replyItem["content"] = reply.css("p.sele_txt::text").get().strip()
            replyItem["addtime"] = reply.css(
                "div.doc_t_strip div.zwAll p::text").get()

            item["askList"].append(replyItem)

        print("wenda: ", item)

        yield item

    def parse_article(self, response):

        item = ArticleItem()
        item["imageList"] = []

        def extract_with_css(query):
            return response.css(query).get(default="").strip()
        item["keyword"] = response.xpath(
            "//meta[@name='keywords']/@content").extract()[0]
        item["description"] = response.xpath(
            "//meta[@name='description']/@content").extract()[0]
        item["title"] = extract_with_css(
            "div.art_box h1::text")
        item["author"] = ""
        item["source"] = response.request.url

        ptags = response.xpath(
            './/div[@class="art_con"]/p')

        # content
        text = []
        for p in ptags:
            # TODO: check .// and //
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        item["content"] = content

        # images
        images = response.xpath(
            './/div[@class="art_con"]//img')

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        page_base_url = ""
        page_count = 0

        if response.css("div.art_page"):
            page_end_url = response.xpath(
                '//div[@class="art_page"]//a/@href').extract()[-1]
            page_base_url, page_count = regex.findall(
                '(.*?)_(.*?).html', page_end_url)[0]
            page_count = int(page_count)
        elif response.css("div.art_con + div.atp_yema"):
            page_end_url = response.css(
                'div.art_con + div.atp_yema a::attr(href)').extract()[-1]
            page_base_url, page_count = regex.findall(
                '(.*?)_(.*?).html', page_end_url)[0]
            page_count = int(page_count)

        for page in range(1, page_count + 1):
            url = page_base_url + '_{}.html'.format(page)
            request = scrapy.Request(
                url=url, callback=self.parse_content, priority=-page)
            request.meta["item"] = item
            request.meta["page_count"] = page_count
            request.meta["page"] = page
            yield request

    # https: // www.jianshu.com/p/3810309e3f54
    def parse_content(self, response):
        item = response.meta["item"]
        page_count = response.meta["page_count"]
        page = response.meta["page"]

        ptags = response.xpath(
            '//div[@class="art_con"]/p')

        text = []
        for p in ptags:
            text.append(p.xpath("string()").extract()[0].strip())

        content = "<br>".join(text)

        item["content"] += content

        images = response.xpath(
            '//div[@class="art_con"]//img')

        for img in images:
            img_url = img.xpath('./@src').extract()[0] or ''
            item["imageList"].append(img_url)

        if page == page_count:
            yield item
