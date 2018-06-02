#-*- coding: UTF-8 -*-   
#!/usr/bin/python
import scrapy
from scrapy.selector import Selector
import json
from xianhua import mongoClient
import logging
from datetime import timezone,timedelta
import datetime

class DmozSpider(scrapy.Spider):
    name = "huazuimei"
    logger = logging.getLogger(__name__)
    def start_requests(self):
        url = "http://www.ynhzm.com/home/GetT_W_FlowerList?SeachStr="
        # FormRequest 是Scrapy发送POST请求的方法
        yield scrapy.FormRequest(
            url = url,
            # meta={'proxy': 'http://127.0.0.1:8888'},
            headers={"X-Requested-With":"XMLHttpRequest",
            "Origin":"http://www.ynhzm.com",
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E302 MicroMessenger/6.6.6 NetType/WIFI Language/zh_CN",
            "Referer":"http://www.ynhzm.com/home/ClassList"
            },
            cookies={'ASP.NET_SessionId':'mrincirzipg320l5xycwmh0g',
            'SERVERID':'cf7be8aa18c15ddcefed599f9fdb40af|1527840293|1527840231',
            'resolution':'736'},
            method='POST',
            callback = self.parse
        )
    def __init__(self):
        client = mongoClient.localMongoClient()
        self.db = client["xianhua"]
        self.collection = self.db['xianhua']
        # self.logger = logging.getLogger("test")
    
    def parse(self, response):
        print ('start to crawl.....')
        print (response.body)