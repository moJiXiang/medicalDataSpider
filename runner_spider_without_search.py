from medicalDataSpider.spiders.lamaquan import LamaquanSpider
from medicalDataSpider.spiders.icheruby import IcherubySpider
from medicalDataSpider.spiders.chaonei import ChaoneiSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

configure_logging()
process = CrawlerRunner(get_project_settings())

process.crawl(ChaoneiSpider)
process.crawl(IcherubySpider)
process.crawl(LamaquanSpider)
d = process.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()
