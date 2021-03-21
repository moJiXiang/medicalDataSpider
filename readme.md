1. docker run -p 8050:8050 --memory=4.5G  --restart=always scrapinghub/splash --disable-private-mode --max-timeout 3600 --maxrss 4000
2. scrapy crawl haodaifu_spider -a keyword=xxx

### 执行
3. sh ./start.sh 崴脚

- [x] 完成从好医生抓取文章数据，并且保存到数据库中
- [x] 将关键词作为爬虫的一个输入参数
- [ ] 将每次爬取的关键词也保存到数据库中
- [ ] 实现关键词查询接口，如果数据库中存在关键词相关的数据，则直接返回结果列表，如果没有则利用爬虫爬取100条数据
- [ ] 将整套业务部署在外网

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