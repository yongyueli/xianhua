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
    name = "xianhua"
    start_urls = [
        "https://shop19448706.youzan.com/v2/feature/svr5sszn?sf=wx_sm&is_share=1&from=groupmessage&isappinstalled=0"
    ]
    logger = logging.getLogger(__name__)
    def __init__(self):
        client = mongoClient.localMongoClient()
        self.db = client["xianhua"]
        self.collection = self.db['xianhua']
        # self.logger = logging.getLogger("test")
        
    def parseItem(self,response):
        # print("-----------------------------------------------")
        # print(response.body)
        json_obj = json.loads(response.body.decode('utf-8'))
        json_obj['date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
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
                yield scrapy.http.Request(url ,headers = headers,cookies={'KDTSESSIONID':'YZ447127244532359168YZRuMrB8JI'},meta={'id': id,'title':title,'alias':alias,'tag_name':response.meta['tag_name']},callback=self.parseFlower)

        self.db['items'].insert(json_obj)

    def parseFlower(self,response):
        # print("-----------------------------------------------")
        # js_code = response.xpath("//script[contains(., '_global ')]/text()").extract_first()
        # js_code = js_code.replace('var _global = ','')
        # js_code = js_code.strip('; ')
        # flower_obj = json.loads(js_code)
        flower = json.loads(response.body.decode('utf-8'))
        flower['tag_name'] = response.meta['tag_name']
        flower['title'] = response.meta['title']
        flower['alias'] = response.meta['alias']
        flower['date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.db['flowers'].insert(flower)

        cateMap = {}
        data = flower['data']
        tree = data['tree']
        sold_num = data['sold_num']
        itemList = data['list']
        title = flower['title']
        tag_name = flower['tag_name']
        for cate in tree:
            catev = cate['v']
            k = cate['k']
            for cateItem in catev:
                cateMap[cateItem['id']] = {'name':cateItem['name'],'category_name':k}
                
        for item in itemList:
            try:
                s1 = item.get('s1')
                s2 = item.get('s2')
                s3 = item.get('s3')
                out_item = {}
                if s1 != '0':
                    out_item[cateMap[s1]['category_name'].replace('选择','')] = cateMap[s1]['name']
                if s2 != '0':
                    out_item[cateMap[s2]['category_name'].replace('选择','')] = cateMap[s2]['name']
                if s3 != '0':
                    out_item[cateMap[s3]['category_name'].replace('选择','')] = cateMap[s3]['name']
                out_item['id'] = item.get('id')
                out_item['goods_id'] = item.get('goods_id')
                out_item['tag_name'] = tag_name
                out_item['sub_tag_name'] = title
                out_item['price'] = item['price'] / 100
                out_item['discount'] = item['discount'] / 100
                out_item['stock_num'] = item['stock_num']
                out_item['sold_num'] = sold_num
                out_item['alias'] = response.meta['alias']
                out_item['date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                self.db['flowers_format'].insert(out_item)
            except :
                print ('something sames wrong...')

    def parse(self, response):
        print ('start to crawl.....')
        filename = response.url.split("/")[-2]
        if(filename == 'feature'):
            js_code = response.xpath("//script[contains(., '_global ')]/text()").extract_first()
            js_code = js_code.replace('var _global = ','')
            js_code = js_code[0:-1]
            tags = json.loads(js_code)
            tags['date'] = datetime.datetime.utcnow().strftime('%Y-%m-%d')
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
