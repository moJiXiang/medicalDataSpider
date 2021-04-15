from medicalDataSpider.spiders.lamaquan import LamaquanSpider
from medicalDataSpider.spiders.icheruby import IcherubySpider
from medicalDataSpider.spiders.chaonei import ChaoneiSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from keywords import keywords

configure_logging()
process = CrawlerProcess(get_project_settings())

process.crawl(ChaoneiSpider)
process.crawl(IcherubySpider)
process.crawl(LamaquanSpider)
process.start()
