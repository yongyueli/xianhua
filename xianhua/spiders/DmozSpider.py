import scrapy
from scrapy.selector import Selector
import json
from xianhua import mongoClient
import logging
from datetime import timezone,timedelta
import datetime

class DmozSpider(scrapy.Spider):
    name = "xianhua"
    start_urls = [
        "https://shop19448706.youzan.com/v2/feature/svr5sszn?sf=wx_sm&is_share=1&from=groupmessage&isappinstalled=0"
    ]
    logger = logging.getLogger(__name__)
    def __init__(self):
        client = mongoClient.defaultMongoCient()
        self.db = client["xianhua"]
        self.collection = self.db['xianhua']
        # self.logger = logging.getLogger("test")
        
    def parseItem(self,response):
        # print("-----------------------------------------------")
        # print(response.body)
        json_obj = json.loads(response.body)
        json_obj['date'] = datetime.datetime.utcnow()
        json_obj['tag_name'] = response.meta['tag_name']
        json_obj['tag_id'] = response.meta['tag_id']
        data = json_obj['data']
        first = data[0]
        for key in first:
            value = first[key]
            for flower in value:
                title = flower['title']
                id = flower['id']
                alias = flower['alias']
                url = 'https://shop19448706.youzan.com/v2/showcase/sku/skudata.json?alias=%s'%(alias)
                print (key,title,url)
                headers = {
                    'accept-language': 'zh-CN,zh;q=0.8',
                    'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E302 MicroMessenger/6.6.6 NetType/WIFI Language/zh_CN',
                }
                yield scrapy.http.Request(url ,headers = headers,cookies={'KDTSESSIONID':'YZ447127244532359168YZRuMrB8JI'},meta={'id': id,'title':title,'tag_name':response.meta['tag_name']},callback=self.parseFlower)

        self.db['items'].insert(json_obj)

    def parseFlower(self,response):
        # print("-----------------------------------------------")
        # js_code = response.xpath("//script[contains(., '_global ')]/text()").extract_first()
        # js_code = js_code.replace('var _global = ','')
        # js_code = js_code.strip('; ')
        # flower_obj = json.loads(js_code)
        flower_obj = json.loads(response.body)
        flower_obj['tag_name'] = response.meta['tag_name']
        flower_obj['title'] = response.meta['title']
        self.db['flowers'].insert(flower_obj)
        


    def parse(self, response):
        print ('start to crawl.....')
        filename = response.url.split("/")[-2]
        if(filename == 'feature'):
            js_code = response.xpath("//script[contains(., '_global ')]/text()").extract_first()
            js_code = js_code.replace('var _global = ','')
            js_code = js_code[0:-1]
            tags = json.loads(js_code)
            tags['date'] = datetime.datetime.utcnow()
            self.collection.insert(tags)
            components = tags.get('components')
            sub_entry = components[3].get('sub_entry')
            for entry in sub_entry:
                goods_num_display = entry.get('goods_num_display')
                h5_url = entry.get('url')
                tag = h5_url.split("alias=")[1]
                tag_name = entry.get('title')
                tag_id = entry.get('id')
                url = "https://shop19448706.youzan.com/v2/showcase/goods/briefGoodsWithTags.json?perpage=%s&tag_alias[]=%s" % (goods_num_display,tag)
                yield scrapy.http.Request(url ,meta={'tag': tag,'tag_name':tag_name,'tag_id':tag_id},callback=self.parseItem)
