
from medicalDataSpider.spiders.bozhong import BozhongSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from keywords import keywords
from short_keywords import short_keywords

configure_logging()
process = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    for keyword in keywords:
        yield process.crawl(BozhongSpider, keyword)

    reactor.stop()


crawl()
reactor.run()
