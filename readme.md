1. docker run -p 8050:8050 --memory=4.5G  --restart=always scrapinghub/splash --disable-private-mode --max-timeout 3600 --maxrss 4000


设置 proxy
https://juejin.cn/post/6844904160727400455

https://ip.jiangxianli.com/?page=1

https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/

https://free-proxy-list.net/


### 问题
1. 百度百科抓不到 赞数据

https://stackoverflow.com/questions/51483008/scrapy-splash-not-rendering-dynamic-content-from-a-certain-react-driven-site


2. Splash with dynamic page
https://stackoverflow.com/questions/51483008/scrapy-splash-not-rendering-dynamic-content-from-a-certain-react-driven-site

### 运行爬虫

sh start_spider.sh sougou_spider 试管婴儿

知乎 不需要 --disable-private-mode
百度百科需要 --disable-private-mode

运行runner_spider.py： python3 runner_spider.py

### 重爬
[x] sougou_spider
[x] lamaquan_spider
[x] ask120_spider
[x] babytree_spider
[x] baidu_baike
[x] baidu_zhidao
[x] bozhong_spider
[x] chaonei
[x] fh21
[x] haodaifu
[x] icheruby
[x] jianshu
[x] shiguanzhijia
[x] tm51
[x] so39
[x] so99
[x] sougou
[x] yunivf
[ ] zhihu


带搜索的
ask120
babytree
bozhong
fh21
haodaifu
jianshu
shiguanzhijia
so39
so99
sougou
tm51
yunivf
zhihu


baidu_baike
baidu_zhidao

没有搜索的

chaonei
icheruby
lamaquan


### 部署
1. 在 --disable-private-mode 模式下运行 python3 runner_baidu_spider.py 
2. 带搜索的爬虫 python3 runner_spider_with_search.py
3. 不带搜索的爬虫 python3 runner_spider_without_search.py
