from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
import pymysql


# Main 화면 구성 - 4개의 프레임
# 1. 숫자 n을 입력하면 최근 n일 동안의 전체 사용률 추이 검색
# 2. 지금 시점에서 대기, 충전중, 통신두절, 고장 충전기 비율 조회
# 3. 지역명을 입력하면 해당 지역의 충전기 10개 이내 조회
# 4. 숫자를 입력하면 그 숫자에 해당하는 구역수를 가진 사용률 히스토그램 출력

root = Tk()
root.geometry("400x600")
root.title("CPS Lab")
mimg = PhotoImage(file="ele.png")


s = ttk.Style()
s.theme_use('default')
s.configure('TNotebook.Tab', background='skyblue')

tabControl = ttk.Notebook(root)
tab1 = Frame(tabControl,background="white")
tab2 = Frame(tabControl,background="white")
tab3 = Frame(tabControl,background="white")
tab4 = Frame(tabControl,background="white")
tabControl.add(tab1, text="Utilization")
tabControl.add(tab2, text="Status")
tabControl.add(tab3, text="Region")
tabControl.add(tab4, text="Distribution")
tabControl.pack(expand=1, fill="both")

# MySQL에서 조회하는 함수: query를 입력받아 수행하고 결과를 리턴
def FromDb(q):
	dbdb = pymysql.connect(user='ev', passwd='ev', 
		host='127.0.0.1', db='ev', charset='utf8')

	cursor = dbdb.cursor()
	cursor.execute(q)

	rec = cursor.fetchall()
	cursor.close()
	dbdb.close()
	return rec

# First Tab
# submit 버튼이 눌리면 수행됨. 여러 query를 순차적으로 mysql에 보냄
def btn1Proc():
	ll=txt1.get()	# 최근 며칠..간 사용률 변화

	query = " drop table if exists tt1; "
	res = FromDb(query)

	query = "create table tt1 "
	query += "select date(ts) as ds, count(*) as cnt "
	query += "from OpStatus "
	query += "group by ds; "
	res = FromDb(query)
	print("Step 1")

	query = "drop table if exists tt2; "
	res = FromDb(query)

	query = "create table tt2 "
	query += "select date(ts) as ds, count(*) as cnt "
	query += "from OpStatus "
	query += "where onoff=2 "
	query += "group by ds; "
	res = FromDb(query)
	print("Step 2")

	query = "select tt1.ds, tt2.cnt/tt1.cnt  "
	query += "from tt1 left join tt2  "
	query += "on tt1.ds=tt2.ds "
	query += "order by ds desc limit "
	query += str(ll)
	query += ";"
#	print(query)
	res = FromDb(query)
	print("Joined")

#	print(res)
	tt =[]
	for i in range(len(res)):
		tt.append(res[i][1])
	xx = list(range(len(tt)))	
	plt.figure(figsize=(4.0, 4.5))
	plt.plot(xx, tt)
	plt.savefig('kaka.png')
	plt.close()

	gimg = PhotoImage(file="kaka.png")
	lbl1.configure(image=gimg)
	lbl1.image =gimg

# 첫번째 탭의 화면 구성
lbl1 = Label(tab1, image=mimg)
lbl1.pack()
txt1 = Entry(tab1)
txt1.pack()
btn1 = Button(tab1, text='Submit', comman=btn1Proc, bg="skyblue")
btn1.pack()



#Second Tab
# submit 버튼이 눌리면 수행
# 가장 최신 날짜의 전체 충전기 상태를 조회 - 대기, 충전중, 통신장애, 고장
def btn2Proc():
	ll=['Wait', 'On', 'Disconnected', 'Failure']
	colors=['plum','darkorange','gray','red']
	
	query =  "select onoff, count(*) from OpStatus "
	query += "where date(ts) = (select Max(date(ts)) from OpStatus)" 
	query += "group by onoff;"
	print(query)
	res = FromDb(query)
#	print(res)
	tt =[]
	for i in range(len(res)):
		tt.append(res[i][1])
	
	if (len(tt) != 4):
		tt.append(0)
	print(tt)
	
	explode = (0.05, 0.05, 0.15,0.35) 
	plt.figure(figsize=(4.0, 4.5))
	plt.pie(tt,explode=explode, labels=ll, startangle=260, counterclock=False,colors=colors)
	plt.savefig('kaka.png')
	plt.close()

	gimg = PhotoImage(file="kaka.png")
	lbl2.configure(image=gimg)
	lbl2.image =gimg


# 두번째 탭의 화면 구성
lbl2 = Label(tab2, image=mimg)
lbl2.pack()
btn2 = Button(tab2, text='Submit', comman=btn2Proc, bg="skyblue")
btn2.pack()


# Third Tab
# 문자를 받아 그 문자를 포함하는 주소들을 검색
# 최대 10개까지 조회, 변경 가능
def btn3Proc():
	res=txt3.get()
	query = "select addr from chargers where addr like "
	query = query + " '%"+res+"%' limit 10;"
	res  = FromDb(query)
	addr = ""
	for i in range(len(res)):
		addr += res[i][0]+"\n"
	lbl3.configure(text=addr)


# 세번째 탭의 화면 구성
lbl3 = Label(tab3, text="\n\n\nPress submit\n\n\n",bg ="white")
lbl3.pack()
txt3 = Entry(tab3)
txt3.pack()
btn3 = Button(tab3, text='Submit', comman=btn3Proc,bg="skyblue")
btn3.pack()


# Fourth Tab
# 충전기 별로 사용율을 구한 후 히스토그램을 생성
# 입력된 숫자는 bin의 개수임, bin이 클수록 세분화
def btn4Proc():
	ll=txt4.get()
	query = " drop table if exists tt1; "
	res = FromDb(query)

	query = "create table tt1 "
	query += "select station, charger, count(*) as cnt "
	query += "from OpStatus "
	query += "group by station, charger; "
	res = FromDb(query)
	print("Step 1")

	query = "drop table if exists tt2; "
	res = FromDb(query)

	query = "create table tt2 "
	query += "select station, charger, count(*) as cnt "
	query += "from OpStatus "
	query += "where onoff=2 "
	query += "group by station, charger; "
	res = FromDb(query)
	print("Step 2")

	query = "select tt2.cnt/tt1.cnt  "
	query += "from tt1 left join tt2  "
	query += "on tt1.station=tt2.station and tt1.charger=tt2.charger ;"
	print(query)
	res = FromDb(query)
	print("Joined")

	tt =[]
	for i in range(len(res)):
		if (res[i][0]== None):	# 결과없음
			tt.append(0)
		else:
			tt.append(res[i][0])

	plt.figure(figsize=(4.0, 4.5))
	plt.hist(tt, bins=int(ll), density=False, color='orange', rwidth=0.5)
	plt.savefig('kaka.png')
	plt.close()

	gimg = PhotoImage(file="kaka.png")
	lbl4.configure(image=gimg)
	lbl4.image =gimg

# 네번째 탭의 화면 구성
lbl4 = Label(tab4, image=mimg)
lbl4.pack()
txt4 = Entry(tab4)
txt4.pack()

btn4 = Button(tab4, text='Submit', comman=btn4Proc,bg="skyblue")
btn4.pack()


# Main loop, 생성한 창을 띄움
root.mainloop()  
