from medicalDataSpider.spiders.lamaquan import LamaquanSpider
from medicalDataSpider.spiders.icheruby import IcherubySpider
from medicalDataSpider.spiders.chaonei import ChaoneiSpider
from medicalDataSpider.spiders.zhihu import ZhihuSpider
from medicalDataSpider.spiders.yunivf import YunivfSpider
from medicalDataSpider.spiders.tm51 import Tm51Spider
from medicalDataSpider.spiders.sougou import SougouSpider
from medicalDataSpider.spiders.so99 import So99Spider
from medicalDataSpider.spiders.so39 import So39Spider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from keywords import keywords

# configure_logging()
process = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield process.crawl(ChaoneiSpider)
    yield process.crawl(IcherubySpider)
    yield process.crawl(LamaquanSpider)

    reactor.stop()


crawl()
reactor.run()
