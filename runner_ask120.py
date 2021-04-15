from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from medicalDataSpider.spiders.ask120 import Ask120Spider
from scrapy.utils.log import configure_logging
from keywords import keywords

configure_logging()
process = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    for keyword in keywords:
        yield process.crawl(Ask120Spider, keyword)

    reactor.stop()


crawl()
reactor.run()
