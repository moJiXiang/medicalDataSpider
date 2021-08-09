from medicalDataSpider.spiders.baidu_zhidao import BaiduZhidaoSpider
from medicalDataSpider.spiders.baidu_baike import BaiduBaikeSpider
from medicalDataSpider.spiders.lamaquan import LamaquanSpider
from medicalDataSpider.spiders.icheruby import IcherubySpider
from medicalDataSpider.spiders.chaonei import ChaoneiSpider
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from keywords import keywords
from short_keywords import short_keywords
import requests

# configure_logging()
process = CrawlerRunner(get_project_settings())

api = "https://spider-es-jx-api.jxivf.com/ex/spider/getNeedCrawlerKeyword"

r = requests.post(api, json={
    "id": 1,
    "pageNum":1,
    "pageSize": 100000
})

re = r.json()

kws = re.get('data')

for kw in kws:
    print(kw.get("title"))
    keywords.append(kw.get("title"))


@defer.inlineCallbacks
def crawl():
    for keyword in keywords:
        yield process.crawl(BaiduBaikeSpider, keyword)
        yield process.crawl(BaiduZhidaoSpider, keyword)

    reactor.stop()


crawl()
reactor.run()
