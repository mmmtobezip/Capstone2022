import requests
import datetime
import time
#url = 'http://openapi.kepco.co.kr/service/EvInfoServiceV2/getEvSearchList'
url = 'http://apis.data.go.kr/B552584/EvCharger/getChargerStatus'

params ={'serviceKey' : 'pzu8M6kHuMVoSmGMVoV8OFf4f7A0X1SgPoIf2PYEyM/z1+Yk5jEpkEmIE7yEkPlkyTO54QqOpnFdKQOucl5DvA==', 'pageNo' : '1', 'numOfRows' : '600', 'addr' : '제주' }

response = requests.get(url, params=params)

#print(response.content)
from bs4 import BeautifulSoup
wsoup = BeautifulSoup(response.text, 'html.parser')
res = wsoup.find_all('item')

#print(res)

cur= datetime.datetime.now()
#print("Cur", cur)
cur1 = cur.strftime("%Y-%m-%d %H:%M:%S")
#print("String1", cur)
cur = time.strptime(cur1, "%Y-%m-%d %H:%M:%S")
#print("String2", cur)
t1 = time.mktime(cur)

F= ['statId', 'chgerId', 'stat']
mval = []
for n in res:
    flist = []
#   tt = n.select_one('statUpdateDatetime')
    tt = n.select_one('statUpdDt')
    a = tt.get_text()
 #  print("Web", ts)	
    ts = (int(a[0:4]), int(a[4:6]), int(a[6:8]), int(a[8:10]), int(a[10:12]), int(a[12:14]), 0,0,0)
    print(ts)
    t2 = time.mktime(ts)	
    dd = (t1-t2)//60	
#    print(dd)	
    if (dd >=60):		
        continue	
    for i in range(len(F)):		
        tt = n.select_one(F[i])			
        flist.append("'"+tt.get_text()+"'")	

    flist.append("'"+cur1+"'")
#   print("insert into OpStatus values("+ ', '.join(flist) + ");")	
    mval.append("("+ ', '.join(flist) + ")")

'''
print("insert into OpStatus values", end='')
print(', '.join(mval), end='')
print(";")	
'''

stmt= "insert into OpStatus values"+ ', '.join(mval)+";"
print(stmt)

import pymysql
conn = pymysql.connect(host='localhost', user='ev', password='ev', db='ev', charset='utf8')
curs = conn.cursor()
curs.execute(stmt)
conn.commit()
#rows = curs.fetchall()
#print(rows)

conn.close()
