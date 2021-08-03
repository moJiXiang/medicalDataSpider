from medicalDataSpider.spiders.zhihu import ZhihuSpider
from medicalDataSpider.spiders.yunivf import YunivfSpider
from medicalDataSpider.spiders.tm51 import Tm51Spider
from medicalDataSpider.spiders.sougou import SougouSpider
from medicalDataSpider.spiders.so99 import So99Spider
from medicalDataSpider.spiders.so39 import So39Spider
from medicalDataSpider.spiders.shiguanzhijia import ShiguanZhijiaSpider
from medicalDataSpider.spiders.jianshu import JianshuSpider
from medicalDataSpider.spiders.haodaifu import HaodaifuSpider
from medicalDataSpider.spiders.fh21 import Fh21Spider
from medicalDataSpider.spiders.bozhong import BozhongSpider
from medicalDataSpider.spiders.babytree import BabytreeSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from medicalDataSpider.spiders.ask120 import Ask120Spider
from scrapy.utils.log import configure_logging
from keywords import keywords
from short_keywords import short_keywords

# configure_logging()
process = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    for keyword in keywords:
        yield process.crawl(Fh21Spider, keyword)
        yield process.crawl(HaodaifuSpider, keyword)
        yield process.crawl(JianshuSpider, keyword)
        yield process.crawl(ShiguanZhijiaSpider, keyword)

    reactor.stop()


crawl()
reactor.run()
