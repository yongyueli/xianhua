import xlwt
import os
import mongoClient
import datetime
import mail

def addHead(workbook):
    sheet1 = workbook.add_sheet('flowers',cell_overwrite_ok=True) ##第二参数用于确认同一个cell单元是否可以重设值。
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
    return sheet1

def getCollection():
    client = mongoClient.defaultMongoCient()
    db = client['xianhua']
    coll = db['flowers_format']
    return coll

def fillSheet(coll,sheet1,today_date,yestoday_date):
    index = 1
    for goods_id in coll.distinct('goods_id',{'date':today_date}):
        for doc in coll.find({'goods_id':goods_id,'date':today_date}):
            sheet1.write(index, 0, doc['tag_name'])
            sheet1.write(index, 1, doc['sub_tag_name'])
            sheet1.write(index, 2, doc.get('颜色',''))
            sheet1.write(index, 3, doc.get('花苞',''))
            sheet1.write(index, 4, doc.get('等级',''))
            sheet1.write(index, 5, doc.get('price',''))
            sheet1.write(index, 6, doc.get('stock_num',''))
            yest_doc = coll.find_one({'date':yestoday_date,'id':doc['id']})
            if yest_doc == None:
                yest_doc = {}
            sheet1.write(index, 7, doc.get('sold_num',0) - yest_doc.get('sold_num',0))
            sheet1.write(index, 8, yest_doc.get('price',''))
            sheet1.write(index, 9, (doc.get('price',0) - yest_doc.get('price',0)))
            index = index + 1
        # sheet1.write_merge(i - count,i - 1,0,0,tag_name)
        # sheet1.write_merge(i - count,i - 1,1,1,sub_tag_name)

#init
today_date = datetime.datetime.now().strftime('%Y-%m-%d')
yest_date = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
path=os.path.join(os.getcwd(),today_date + '.xls')
workbook = xlwt.Workbook()  # 创建工作簿
coll = getCollection()

#fille sheet and save file
sheet1 = addHead(workbook)
fillSheet(coll,sheet1,today_date,yest_date)
workbook.save(path)

#send mail
mail.send_mail(subject = '花库数据统计' + today_date,message = 'Hi all,\n附件中是今天的花库数据统计，请查收',files=[path])