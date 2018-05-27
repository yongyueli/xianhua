import xlwt
import os
import mongoClient
import datetime
import mail
f = xlwt.Workbook()  # 创建工作簿
now_time = datetime.datetime.now().strftime('%Y-%m-%d')
path=os.path.join(os.getcwd(),now_time + '.xls')

sheet1 = f.add_sheet('flowers',cell_overwrite_ok=True) ##第二参数用于确认同一个cell单元是否可以重设值。
sheet1.write(0, 0, '一级分类')
sheet1.write(0, 1, '二级分类')
sheet1.write(0, 2, '颜色')
sheet1.write(0, 3, '花苞')
sheet1.write(0, 4, '等级')
sheet1.write(0, 5, '价格')
sheet1.write(0, 6, '剩余')
sheet1.write(0, 7, '昨日销量')
sheet1.write(0, 8, '昨日价格')
sheet1.write(0, 9, '价格变化率')

client = mongoClient.defaultMongoCient()
db = client['xianhua']
coll = db['flowers_format']
i = 1
for goods_id in coll.distinct('goods_id'):
    count = coll.count({'goods_id':goods_id})
    tag_name = ''
    sub_tag_name = ''
    for doc in coll.find({'goods_id':goods_id}):
        tag_name = doc['tag_name']
        sub_tag_name = doc['sub_tag_name']
        sheet1.write(i, 0, doc['tag_name'])
        sheet1.write(i, 1, doc['sub_tag_name'])
        sheet1.write(i, 2, doc.get('颜色',''))
        sheet1.write(i, 3, doc.get('花苞',''))
        sheet1.write(i, 4, doc.get('等级',''))
        sheet1.write(i, 5, doc.get('price',''))
        sheet1.write(i, 6, doc.get('stock_num',''))
        yest_date = datetime.datetime.now() + datetime.timedelta(days=-1)
        yest_doc = coll.find_one({'date':yest_date.strftime('%Y-%m-%d')})
        if yest_doc == None:
            yest_doc = {}
        sheet1.write(i, 7, doc.get('sold_num',0) - yest_doc.get('sold_num',0))
        sheet1.write(i, 8, yest_doc.get('price',''))
        sheet1.write(i, 9, (doc.get('price',0) - yest_doc.get('price',0)) / doc.get('price',1))
        i = i + 1
    # sheet1.write_merge(i - count,i - 1,0,0,tag_name)
    # sheet1.write_merge(i - count,i - 1,1,1,sub_tag_name)
f.save(path)
files = [path]
mail.send_mail(subject = 'flowers-' + now_time,files=files)