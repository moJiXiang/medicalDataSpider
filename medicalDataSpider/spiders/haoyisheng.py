from scrapy.spiders import Spider

class BlogSpider(Spider):
  # 爬虫名称
  name = "quotes"
  # 爬虫真实的爬取url
  start_urls = [
    'https://so.haodf.com/index/search?kw=%E8%AF%95%E7%AE%A1',
  ]

  # 网页响应解析
  def parse(self, response):
    # for wenzhang in response.css("div.sc-wenzhang"):
    #     yield {
    #       "title": wenzhang.xpath('string(.//div[@class="sc-wz-title"]/span/a)').extract()[0],
    #     }

    # 根据分页数据构造url
    total = response.css("div.ctn-page div.g-page")
    print("Total: ", total)
    next_page = response.css("div.g-page a[data-pager-link='next']::attr(href)").get()
    print("Next page: ", next_page)
    if next_page is not None:
      yield response.follow(next_page, callback=self.parse)

class AuthorSpider(Spider):
  name = "author"

  start_urls = ['http://quotes.toscrape.com/']

  def parse(self, response):
    author_page_links = response.css(".author + a")
    yield from response.follow_all(author_page_links, self.parse_author)

    pagination_links = response.css("li.next a")
    yield from response.follow_all(pagination_links, self.parse)

  def parse_author(self, response):
    def extract_with_css(query):
        return response.css(query).get(default="").strip()
    
    yield {
      "name": extract_with_css("h3.author-title::text"),
      'birthdate': extract_with_css('.author-born-date::text'),
      'bio': extract_with_css('.author-description::text'),
    }