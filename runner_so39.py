from medicalDataSpider.spiders.so39 import So39Spider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from keywords import keywords

configure_logging()
process = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    for keyword in keywords:
        yield process.crawl(So39Spider, keyword)

    reactor.stop()


crawl()
reactor.run()
