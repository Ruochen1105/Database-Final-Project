#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import hashlib
import matplotlib.pyplot as plt
import datetime
import pandas as pd

def dif(lissy1,lissy2):
	#find the shared elements between two lists
	result=list()
	for i in lissy1:
		if i in lissy2:
			result.append(i)
	return result

#Initialize the app from Flask
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#Configure MySQL
conn = mysql.connector.connect(host='localhost',
                       user='root',
                       password='',
                       database='ticket')
@app.route('/purchase_c',methods=['GET','POST'])
def purchase():
	an=request.form['an']
	fn=request.form['fn']
	today=(datetime.datetime.today())
	qqueryy="select departure_time from flight where flight.airline_name=%s and flight.flight_num=%s" 
	cursor=conn.cursor()
	cursor.execute(qqueryy,(an,fn))
	dt=cursor.fetchone()[0]
	if today>=dt:
		flash('You can\'t buy expired ticket.')
		return render_template('logged_c.html')
	qquery="select count(ticket_id) from ticket where airline_name=%s and flight_num=%s" 
	queryy="select airplane.seats from (flight inner join airplane on flight.airplane_id=airplane.airplane_id) where flight.airline_name=%s and flight.flight_num=%s" 
	cursor=conn.cursor()
	cursor.execute(qquery, (an,fn))
	a=cursor.fetchone()[0]
	cursor=conn.cursor()
	cursor.execute(queryy, (an,fn))
	b=cursor.fetchone()[0]
	if a>=b:
		flash('No seat available.')
		return render_template('logged_c.html')	
	file=open('counter.txt','r')
	ticket_count=file.readlines()
	ticket_count=[int(i.strip()) for i in ticket_count][0]
	ticket_count+=1
	file.close()
	file=open('counter.txt','w')
	file.write(str(ticket_count))
	file.close()
	cursor=conn.cursor()
	query="insert into ticket values (%s,%s,%s)"
	query1="insert into purchases(ticket_id,customer_email,purchase_date) values (%s,%s,%s)"
	cursor.execute(query , (ticket_count,an,fn,))
	conn.commit()
	cursor=conn.cursor()
	cursor.execute(query1 , (ticket_count,session['username'],str(datetime.date.today()),))
	conn.commit()
	flash('Success!')
	return render_template('logged_c.html',email=session['username'])

@app.route('/purchase_b',methods=['GET','POST'])
def purchaseb():
	cursor=conn.cursor()
	query="select booking_agent_id from booking_agent where email=%s"
	cursor.execute(query , (session['username'],))
	bi=int(cursor.fetchone()[0])#booking agent id
	an=request.form['an']
	fn=request.form['fn']
	today=(datetime.datetime.today())
	qqueryy="select departure_time from flight where flight.airline_name=%s and flight.flight_num=%s" 
	cursor=conn.cursor()
	cursor.execute(qqueryy,(an,fn))
	dt=cursor.fetchone()[0]
	if today>=dt:
		flash('You can\'t buy expired ticket.')
		return render_template('logged_b.html')
	qquery="select count(ticket_id) from ticket where airline_name=%s and flight_num=%s" 
	queryy="select airplane.seats from (flight inner join airplane on flight.airplane_id=airplane.airplane_id) where flight.airline_name=%s and flight.flight_num=%s" 
	cursor=conn.cursor()
	cursor.execute(qquery, (an,fn))
	a=cursor.fetchone()[0]
	cursor=conn.cursor()
	cursor.execute(queryy, (an,fn))
	b=cursor.fetchone()[0]
	print(a,b)
	if a>=b:
		flash('no seat available')
		return render_template('logged_b.html')
	customer=request.form['cust']
	file=open('counter.txt','r')
	ticket_count=file.readlines()
	ticket_count=[int(i.strip()) for i in ticket_count][0]
	ticket_count+=1
	file.close()
	file=open('counter.txt','w')
	file.write(str(ticket_count))
	file.close()
	cursor=conn.cursor()
	query="insert into ticket values(%s,%s,%s)"
	query1="insert into purchases values(%s,%s,%s,%s)"
	try:
		cursor.execute(query , (ticket_count,an,fn,))
		conn.commit()
		cursor=conn.cursor()
		cursor.execute(query1 , (ticket_count,customer,bi,str(datetime.date.today()),))
		conn.commit()
	except:
		flash('Invalid Input!')
		return render_template('logged_b.html',email=session['username'])
	flash('Success!')
	return render_template('logged_b.html',email=session['username'])

@app.route('/VC',methods=['GET','POST'])
def VC():#view customers
	if session['identity']!='s':
		return render_template('error.html')
	an=request.form['an']
	fn=request.form['fn']
	query="""select distinct purchases.customer_email
			from ticket inner join purchases on ticket.ticket_id=purchases.ticket_id
			where ticket.airline_name=%s and ticket.flight_num=%s""" 
	cursor=conn.cursor()
	cursor.execute(query, (an,fn,))
	result=cursor.fetchall()
	return render_template('VC.html',data=result)

@app.route('/lgb')
def lgb():#back to booking agent home page
	try:
		if session['identity']!='b':
			return render_template('error.html')
		return render_template('logged_b.html',email=session['username'])
	except:
		return render_template('error.html')

@app.route('/lgc')
def lgc():#back to customer home page
	try:
		if session['identity']!='c':
			return render_template('error.html')
		return render_template('logged_c.html',email=session['username'])
	except:
		return render_template('error.html')

@app.route('/lgs')
def lgs():#back to staff home page
	try:
		if session['identity']!='s':
			return render_template('error.html')
		return render_template('logged_s.html',email=session['username'])
	except:
		return render_template('error.html')

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login_c')
def login_c():
	return render_template('login_c.html')

@app.route('/login_b')
def login_b():
	return render_template('login_b.html')

@app.route('/login_s')
def login_s():
	return render_template('login_s.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/register_c')
def register_c():
	return render_template('register_c.html')

@app.route('/register_b')
def register_b():
	return render_template('register_b.html')

@app.route('/register_s')
def register_s():
	return render_template('register_s.html')

@app.route('/loginAuth_b', methods=['GET', 'POST'])
def loginAuth_b():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM booking_agent WHERE email = %s and password = %s" 
	cursor.execute(query, (email, hashlib.md5(password.encode()).hexdigest(),))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = email
		session['identity']='b'
		return render_template("logged_b.html",username=email)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

@app.route('/loginAuth_c', methods=['GET', 'POST'])
def loginAuth_c():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM customer WHERE email = %s and password = %s" 
	cursor.execute(query, (email, hashlib.md5(password.encode()).hexdigest(),))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = email
		session['identity']='c'
		return render_template('logged_c.html',username=email)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

@app.route('/loginAuth_s', methods=['GET', 'POST'])
def loginAuth_s():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM airline_staff WHERE username = %s and password = %s" 
	cursor.execute(query, (username, hashlib.md5(password.encode()).hexdigest(),))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		session['identity']='s'
		return render_template('logged_s.html',username=username)
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

@app.route('/registerAuth_b', methods=['GET', 'POST'])
def registerAuth_b():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	booking_agent_id=request.form['booking_agent_id']
	'''
	if not len(password) >= 4:
                flash("Password length must be at least 4 characters")
                return redirect(request.url)
	'''
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM booking_agent WHERE email = %s" 
	cursor.execute(query, (email,))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = "INSERT INTO booking_agent VALUES(%s, %s,%s)" 
		cursor.execute(ins, (email, hashlib.md5(password.encode()).hexdigest(), booking_agent_id,))
		conn.commit()
		cursor.close()
		flash("You are registered.")
		return render_template('index.html')

@app.route('/registerAuth_c', methods=['GET', 'POST'])
def registerAuth_c():
	#grabs information from the forms
	email=request.form['email']
	name = request.form['name']
	password = request.form['password']
	building_number = request.form['building_number']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = request.form['phone_number']
	passport_number = request.form['passport_number']
	passport_expiration = request.form['passport_expiration']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']
	'''
	if not len(password) >= 4:
                flash("Password length must be at least 4 characters")
               return redirect(request.url)
	'''
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM customer WHERE email = %s"
	cursor.execute(query , (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = "INSERT INTO customer VALUES(%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" 
		cursor.execute(ins, (email,name,hashlib.md5(password.encode()).hexdigest(),building_number,street,city,state,phone_number,passport_number,passport_expiration,passport_country,date_of_birth))
		conn.commit()
		cursor.close()
		flash("You are registered.")
		return render_template('index.html')

@app.route('/registerAuth_s', methods=['GET', 'POST'])
def registerAuth_s():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	first_name=request.form['first_name']
	last_name=request.form['last_name']
	date_of_birth=request.form['date_of_birth']
	airline_name=request.form['airline_name']
	'''
	if not len(password) >= 4:
                flash("Password length must be at least 4 characters")
               return redirect(request.url)
	'''
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = "SELECT * FROM airline_staff WHERE username = %s" 
	cursor.execute(query, (username,))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = "INSERT INTO airline_staff VALUES(%s, %s,%s,%s,%s,%s)" 
		try:
			cursor.execute(ins, (username, hashlib.md5(password.encode()).hexdigest(),first_name,last_name,date_of_birth,airline_name,))
			conn.commit()
			cursor.close()
			flash("You are registered.")
			return render_template('index.html')
		except:
			error='invalid input!'
			return render_template('register.html',error=error)

@app.route('/logout')
def logout():
	session.pop('username')
	flash('goodbye')
	return render_template('login.html')

@app.route('/SfF',methods=['GET','POST'])#search for flights
def SfF():
	query="""select *
			from flight"""
	source=request.form['source']
	destination=request.form['destination']
	start=request.form['start']
	end=request.form['end']
	cursor=conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	if source!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
		source1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.departure_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (source,))
		data1 += cursor.fetchall()
		for i in source1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if destination!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
		destination1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.arrival_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (destination,))
		data1 += cursor.fetchall()
		for i in destination1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if start=='' and end=='':
		query1=query
		query1 += " where flight.departure_time >= now()"
		cursor=conn.cursor()
		cursor.execute(query1)
		data1=cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1 += " where flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (start,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1 += " where flight.departure_time <= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (end,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	return render_template('flights.html',data=data)

@app.route('/CFS',methods=['GET','POST'])#check flight status
def CFS():
	fn=request.form['fn']
	start=request.form['start']
	end=request.form['end']
	query="select distinct status from flight"
	cursor=conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	if fn!='':
		query1=query+" where flight_num=%s"
		cursor=conn.cursor()
		cursor.execute(query1 , (fn,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1+=" where date(departure_time)=%s"
		cursor=conn.cursor()
		cursor.execute(query1 , (start,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1+=" where date(arrival_time)=%s"
		cursor=conn.cursor()
		cursor.execute(query1 , (end,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if len(data)==1:
		flash(data[0][0])
	else:
		flash('Invalid Input!')
	return render_template('index.html')

@app.route('/VMF_c', methods=['GET','POST'])#view my flights customer
def VMF_c():
	if session['identity']!='c':
		return render_template('error.html')
	query = """SELECT * FROM 
			((flight inner join ticket on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num) 
				inner join purchases on ticket.ticket_id=purchases.ticket_id) where purchases.customer_email=%s"""
	data=list()
	try:
		upcoming=request.form['upcoming']
	except:
		upcoming=''
	try:
		inprogress=request.form['inprogress']
	except:
		inprogress=''
	try:
		delayed=request.form['delayed']
	except:
		delayed=''
	start=request.form['start']
	end=request.form['end']
	source=request.form['source']
	destination=request.form['destination']
	#checking status
	if upcoming!='':
		cursor=conn.cursor()
		query1=query
		query1 += " and flight.status = %s"
		cursor.execute(query1 , (session['username'],'upcoming'))
		data += cursor.fetchall()
	if inprogress!='':
		cursor=conn.cursor()	
		query1=query
		query1 += " and flight.status = %s"
		cursor.execute(query1 , (session['username'],'in-progress'))
		data += cursor.fetchall()
	if delayed!='':
		cursor=conn.cursor()
		query1=query
		query1 += " and flight.status = %s"
		cursor.execute(query1 , (session['username'],'delayed'))
		data += cursor.fetchall()
	if start=='' and end=='':
		query1=query
		query1 += " and flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (session['username'],str(datetime.datetime.today())))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if source!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
		source1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " and flight.departure_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (session['username'],source))
		data1 += cursor.fetchall()
		for i in source1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],i[0]))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if destination!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
		destination1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " and flight.arrival_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (session['username'],destination))
		data1 += cursor.fetchall()
		for i in destination1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],i[0]))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1 += " and flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (session['username'],start))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1 += " and flight.departure_time <= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (session['username'],end))
		data1=cursor.fetchall()
		data=dif(data,data1)
	return render_template('flights.html',data=data,identity=session['identity'])

@app.route('/VMF_b', methods=['GET','POST'])#view my flights booking agent
def VMF_b():
	if session['identity']!='b':
		return render_template('error.html')
	query = """SELECT * FROM 
			((flight inner join ticket on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num) 
				inner join purchases on ticket.ticket_id=purchases.ticket_id) 
			WHERE purchases.booking_agent_id=%s"""
	try:
		upcoming=request.form['upcoming']
	except:
		upcoming=''
	try:
		inprogress=request.form['inprogress']
	except:
		inprogress=''
	try:
		delayed=request.form['delayed']
	except:
		delayed=''
	source=request.form['source']
	destination=request.form['destination']
	start=request.form['start']
	end=request.form['end']
	data=list()
	cursor = conn.cursor()
	queryy = "select booking_agent_id from booking_agent where email = %s"
	cursor.execute(queryy , (session['username'],))
	id=cursor.fetchone()[0]
	if upcoming!='':
		cursor = conn.cursor()
		query1=query
		query1+=" and flight.status = %s"
		cursor.execute(query1 , (id,'upcoming'))
		data += cursor.fetchall()
	if inprogress!='':
		cursor = conn.cursor()
		query1=query
		query1+=" and flight.status = %s"
		cursor.execute(query1 , (id,'in-progress'))
		data += cursor.fetchall()
	if delayed!='':
		cursor = conn.cursor()
		query1=query
		query1+=" and flight.status = %s"
		cursor.execute(query1 , (id,'delayed'))
		data += cursor.fetchall()
	if source!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
		source1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " and flight.departure_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (id,source))
		data1 += cursor.fetchall()
		for i in source1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (id,i[0]))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if destination!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
		destination1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " and flight.arrival_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (id,destination))
		data1 += cursor.fetchall()
		for i in destination1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (id,i[0]))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1 += " and flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (id,start))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1 += " and flight.departure_time <= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (id,end))
		data1=cursor.fetchall()
		data=dif(data,data1)
	return render_template("flights.html",data=data,identity=session['identity'])

@app.route('/SfF_c', methods=['GET','POST'])#search for flights customer
def SfF_c():
	if session['identity']!='c':
		return render_template('error.html')
	query="""select *
			from flight"""
	source=request.form['source']
	destination=request.form['destination']
	start=request.form['start']
	end=request.form['end']
	cursor=conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	if source!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
		source1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.departure_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (source,))
		data1 += cursor.fetchall()
		for i in source1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if destination!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
		destination1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.arrival_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (destination,))
		data1 += cursor.fetchall()
		for i in destination1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1 += " where flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (start,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1 += " where flight.departure_time <= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (end,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	return render_template('flights.html',data=data,identity=session['identity'],extra='True')

@app.route('/TMS', methods=['GET','POST'])#track my spending
def TMS():
	if session['identity']!='c':
		return render_template('error.html')
	query="""select flight.price, purchases.purchase_date
			from ((flight inner join ticket on flight.flight_num=ticket.flight_num and flight.airline_name=ticket.airline_name)
			inner join purchases on ticket.ticket_id=purchases.ticket_id)
			where purchases.customer_email=%s"""
	start=request.form['start']
	end=request.form['end']
	if start=='' and end=='':
		query1=query
		query1+=" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 6 MONTH)"
		cursor=conn.cursor()
		cursor.execute(query1 , (session['username'],))
		spending=cursor.fetchall()
		query1="""select sum(flight.price)
			from ((flight inner join ticket on flight.flight_num=ticket.flight_num and flight.airline_name=ticket.airline_name)
			inner join purchases on ticket.ticket_id=purchases.ticket_id)
			where purchases.customer_email=%s"""
		query1+=" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)"
		cursor=conn.cursor()
		cursor.execute(query1 , (session['username'],))
		all=cursor.fetchone()[0]
	else:
		cursor=conn.cursor()
		cursor.execute(query , (session['username'],))
		spending=cursor.fetchall()
		all=0
		if start!='':
			query1=query
			query1+=" and purchases.purchase_date>=%s"
			cursor=conn.cursor()
			cursor.execute(query1 , (session['username'],start))
			spending1=cursor.fetchall()
			spending=dif(spending,spending1)
		if end!='':
			query1=query
			query1+=" and purchases.purchase_date<=%s"
			cursor=conn.cursor()
			cursor.execute(query1 , (session['username'],end))
			spending1=cursor.fetchall()
			spending=dif(spending,spending1)
		for i in spending:
			all+=float(i[0])
	sum=dict()
	if len(spending)==0:
		return render_template('TMS.html',total=0)
	for i in spending:
		sum[str(i[1])[:7]]=sum.get(str(i[1])[:7],0)+float(i[0])
	dat=pd.DataFrame(sum.values(),index=sum.keys())
	bar=dat.plot(kind='bar',legend=False,xlabel='month',ylabel='money',figsize=(10,10))
	bar.figure.savefig('static/bar.png')
	return render_template('TMS.html',total=all,identity=session['identity'])

@app.route('/SfF_b', methods=['GET','POST'])#search for flights booking agent
def SfF_b():
	if session['identity']!='b':
		return render_template('error.html')
	query="""select *
			from flight"""
	source=request.form['source']
	destination=request.form['destination']
	start=request.form['start']
	end=request.form['end']
	cursor=conn.cursor()
	cursor.execute(query)
	data=cursor.fetchall()
	if source!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
		source1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.departure_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (source,))
		data1 += cursor.fetchall()
		for i in source1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if destination!='':
		cursor=conn.cursor()	
		cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
		destination1=cursor.fetchall()
		data1=list()
		query1=query
		query1 += " where flight.arrival_airport = %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (destination,))
		data1 += cursor.fetchall()
		for i in destination1:
			cursor=conn.cursor()	
			cursor.execute(query1 , (i[0],))
			data1 += cursor.fetchall()
		data=dif(data,data1)
	if start!='':
		query1=query
		query1 += " where flight.departure_time >= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (start,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	if end!='':
		query1=query
		query1 += " where flight.departure_time <= %s"
		cursor=conn.cursor()	
		cursor.execute(query1 , (end,))
		data1=cursor.fetchall()
		data=dif(data,data1)
	return render_template('flights.html',data=data,identity=session['identity'],extra='True')

@app.route('/VmC', methods=['GET','POST'])#view my commision
def VmC():
	if session['identity']!='b':
		return render_template('error.html')
	query="""select flight.price,ticket.ticket_id
			from ((flight inner join ticket on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num)
			inner join (booking_agent inner join purchases on purchases.booking_agent_id=booking_agent.booking_agent_id) on purchases.ticket_id=ticket.ticket_id)
			where booking_agent.email=%s"""
	start=request.form['start']
	end=request.form['end']
	if start=='' and end=='':
		query1=query
		query1+=" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 30 DAY)"
		cursor=conn.cursor()
		cursor.execute(query1 , (session['username'],))
		commission=cursor.fetchall()
	else:
		cursor=conn.cursor()
		cursor.execute(query , (session['username'],))
		commission=cursor.fetchall()
		if start!='':
			query1=query
			query1+=" and purchases.purchase_date>=%s"
			cursor=conn.cursor()
			cursor.execute(query1 , (session['username'],start))
			commission1=cursor.fetchall()
			commission=dif(commission,commission1)
		if end!='':
			query1=query
			query1+=" and purchases.purchase_date<=%s"
			cursor=conn.cursor()
			cursor.execute(query1 , (session['username'],end))
			commission1=cursor.fetchall()
			commission=dif(commission,commission1)
	if len(commission)!=0:
		count=len(commission)
		total=0.1*sum([float(i[0]) for i in commission])
		avg=total/count
	else:
		count=0
		total=0
		avg=0
	return render_template('VmC.html',total=total,count=count,avg=avg,identity=session['identity'])

@app.route('/VTC', methods=['GET','POST'])#view top customers
def VTC():
	if session['identity']!='b':
		return render_template('error.html')
	cursor = conn.cursor()
	queryy = "select booking_agent_id from booking_agent where email = %s"
	cursor.execute(queryy , (session['username'],))
	id=cursor.fetchone()[0]
	query1="""select count(purchases.ticket_id) as count,purchases.customer_email
			from ((flight inner join ticket on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num)
			inner join (booking_agent inner join purchases on purchases.booking_agent_id=booking_agent.booking_agent_id) on purchases.ticket_id=ticket.ticket_id)
			where purchases.purchase_date>=DATE_SUB(now(), INTERVAL 6 MONTH) and purchases.booking_agent_id=%s
			group by purchases.customer_email
			order by count DESC limit 5""" 
	query2="""select 0.1*sum(flight.price) as aall,purchases.customer_email
			from ((flight inner join ticket on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num)
			inner join (booking_agent inner join purchases on purchases.booking_agent_id=booking_agent.booking_agent_id) on purchases.ticket_id=ticket.ticket_id)
			where purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR) and purchases.booking_agent_id=%s
			group by purchases.customer_email
			order by aall DESC limit 5""" 
	cursor=conn.cursor()
	cursor.execute(query1, (id,))
	customers1=cursor.fetchall()
	cursor=conn.cursor()
	cursor.execute(query2, (id,))
	customers2=cursor.fetchall()
	dat1=pd.DataFrame([i[0] for i in customers1],index=[i[1] for i in customers1])
	bar1=dat1.plot(kind='bar',legend=False,xlabel='customer',ylabel='number of tickets',figsize=(10,10))
	bar1.figure.savefig('static/bar1.png')
	dat2=pd.DataFrame([float(i[0]) for i in customers2],index=[i[1] for i in customers2])
	bar2=dat2.plot(kind='bar',legend=False,xlabel='customer',ylabel='commission earned',figsize=(10,10))
	bar2.figure.savefig('static/bbbar.png')
	return render_template('VTC.html',identity=session['identity'])

@app.route('/VMF_s', methods=['GET','POST'])#view my flights staff
def VMF_s():
	if session['identity']!='s':
		return render_template('error.html')
	query="""select *
			from flight
			where flight.airline_name=(select airline_name from airline_staff where username=%s)
			and """
	start=request.form['start']
	end=request.form['end']
	source=request.form['source']
	destination=request.form['destination']
	if start=='' and end=='':
		query+="(TO_DAYS(flight.departure_time) - TO_DAYS(NOW())) between 0 and 30"
		cursor=conn.cursor()
		cursor.execute(query , (session['username'],))
		data=cursor.fetchall()
		if source!='':
			cursor=conn.cursor()	
			cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
			source1=cursor.fetchall()
			data1=list()
			query1=query
			query1 += " and flight.departure_airport = %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],source))
			data1 += cursor.fetchall()
			for i in source1:
				cursor=conn.cursor()	
				cursor.execute(query1 , (session['username'],i[0]))
				data1 += cursor.fetchall()
			data=dif(data,data1)
		if destination!='':
			cursor=conn.cursor()	
			cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
			destination1=cursor.fetchall()
			data1=list()
			query1=query
			query1 += " and flight.arrival_airport = %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],destination))
			data1 += cursor.fetchall()
			for i in destination1:
				cursor=conn.cursor()	
				cursor.execute(query1 , (session['username'],i[0]))
				data1 += cursor.fetchall()
			data=dif(data,data1)
	else:
		cursor=conn.cursor()
		cursor.execute(query[:-4] , (session['username'],))
		data=cursor.fetchall()
		if source!='':
			cursor=conn.cursor()	
			cursor.execute("select airport_name from airport where airport_city=%s" , (source,))
			source1=cursor.fetchall()
			data1=list()
			query1=query
			query1 += " flight.departure_airport = %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],source,))
			data1 += cursor.fetchall()
			for i in source1:
				cursor=conn.cursor()	
				cursor.execute(query1 , (session['username'],i[0],))
				data1 += cursor.fetchall()
			data=dif(data,data1)
		if destination!='':
			cursor=conn.cursor()	
			cursor.execute("select airport_name from airport where airport_city=%s" , (destination,))
			destination1=cursor.fetchall()
			data1=list()
			query1=query
			query1 += " flight.arrival_airport = %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],destination,))
			data1 += cursor.fetchall()
			for i in destination1:
				cursor=conn.cursor()	
				cursor.execute(query1 , (session['username'],i[0],))
				data1 += cursor.fetchall()
			data=dif(data,data1)
		if start!='':
			query1=query
			query1 += "flight.departure_time >= %s"
			cursor=conn.cursor()
			cursor.execute(query1 , (session['username'],start,))
			data1=cursor.fetchall()
			data=dif(data,data1)
		if end!='':
			query1=query
			query1 += " flight.departure_time <= %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],end,))
			data1=cursor.fetchall()
			data=dif(data,data1)
	return render_template('flights.html',data=data,identity=session['identity'],extra='True')

@app.route('/CNF', methods=['GET','POST'])#create new flights
def CNF():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	cursor.execute("select airline_name from airline_staff where username=%s" , (session['username'],))
	an=cursor.fetchall()[0][0]
	fn=request.form['fn']#flight number
	da=request.form['da']#departure airport
	dt=request.form['dt']#departure time
	aa=request.form['aa']#arrival airport
	at=request.form['at']#arrival time
	p=request.form['p']#price
	s=request.form['s']#status
	ai=request.form['ai']#airplane id
	cursor=conn.cursor()
	query="insert into flight values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	try:
		cursor.execute(query , (an,fn,da,dt,aa,at,p,s,ai))
		conn.commit()
		flash('Success!')
		return render_template('logged_s.html',username=session['username'])
	except:
		flash('Invalid Input!')
		return render_template('logged_s.html',username=session['username'])

@app.route('/CSoF', methods=['GET','POST'])#change status of flights
def CSoF():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	cursor.execute("select airline_name from airline_staff where username=%s" , (session['username'],))
	an=cursor.fetchall()[0][0]
	fn=request.form['fn']#flight number
	st=request.form['st']#status
	cursor=conn.cursor()
	query="""update flight
			set flight.status=%s
			where flight.airline_name=%s and flight.flight_num=%s""" 
	try:
		cursor.execute(query, (st,an,fn))
		conn.commit()
		flash('Success!')
		return render_template('logged_s.html',username=session['username'])
	except:
		flash('Invalid Input!')
		return render_template('logged_s.html',username=session['username'])

@app.route('/AAItS', methods=['GET','POST'])#add airplane in the system
def AAItS():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	cursor.execute("select airline_name from airline_staff where username=%s" , (session['username'],))
	an=cursor.fetchall()[0][0]
	ai=request.form['ai']#airplane id
	seats=request.form['seats']#seats
	cursor=conn.cursor()
	query="insert into airplane values(%s,%s,%s)" 
	try:
		cursor.execute(query, (an,ai,seats))
		conn.commit()
		flash('Success!')
		return render_template('logged_s.html',username=session['username'])
	except:
		flash('Invalid Input!')
		return render_template('logged_s.html',username=session['username'])

@app.route('/ANAItS', methods=['GET','POST'])#add new airport in the system
def ANAItS():
	if session['identity']!='s':
		return render_template('error.html')
	an=request.form['an']#airport name
	ac=request.form['ac']#airport city
	cursor=conn.cursor()
	query="insert into airport values(%s,%s)" 
	try:
		cursor.execute(query, (an,ac))
		conn.commit()
		flash('Success!')
		return render_template('logged_s.html',username=session['username'])
	except:
		flash('Invalid Input!')
		return render_template('logged_s.html',username=session['username'])

@app.route('/VAtBA', methods=['GET','POST'])#view all the booking agents
def VAtBA():
	if session['identity']!='s':
		return render_template('error.html')
	query1="""select count(purchases.ticket_id) as cnt,booking_agent.email
			from ((booking_agent inner join purchases on booking_agent.booking_agent_id=purchases.booking_agent_id)
			inner join (ticket inner join flight on ticket.flight_num=flight.flight_num and ticket.airline_name=flight.airline_name) on purchases.ticket_id=ticket.ticket_id)
			where (purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 MONTH) and ticket.airline_name=(select airline_name from airline_staff where username=%s))
			group by booking_agent.email
			order by cnt DESC limit 5""" 
	query2="""select count(purchases.ticket_id) as cnt,booking_agent.email
			from ((booking_agent inner join purchases on booking_agent.booking_agent_id=purchases.booking_agent_id)
			inner join (ticket inner join flight on ticket.flight_num=flight.flight_num and ticket.airline_name=flight.airline_name) on purchases.ticket_id=ticket.ticket_id)
			where (purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)  and ticket.airline_name=(select airline_name from airline_staff where airline_staff.username=%s))
			group by booking_agent.email
			order by cnt DESC limit 5"""
	query3="""select 0.1*sum(flight.price) as com,booking_agent.email
			from ((booking_agent inner join purchases on booking_agent.booking_agent_id=purchases.booking_agent_id)
			inner join (ticket inner join flight on ticket.flight_num=flight.flight_num and ticket.airline_name=flight.airline_name) on purchases.ticket_id=ticket.ticket_id)
			where (purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR) and ticket.airline_name=(select airline_name from airline_staff where airline_staff.username=%s))
			group by booking_agent.email
			order by com DESC limit 5"""
	cursor=conn.cursor()
	cursor.execute(query1, (session['username'],))
	agents1=cursor.fetchall()
	cursor=conn.cursor()
	cursor.execute(query2, (session['username'],))
	agents2=cursor.fetchall()
	cursor=conn.cursor()
	cursor.execute(query3, (session['username'],))
	agents3=cursor.fetchall()
	return render_template('VAtBA.html',a1=agents1,a2=agents2,a3=agents3,identity=session['identity'])

@app.route('/VFC', methods=['GET','POST'])##view frequent customers
def VFC():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	query="""select count(ticket.ticket_id) as cnt,purchases.customer_email
			from (purchases inner join ticket on purchases.ticket_id=ticket.ticket_id)
			where (select airline_staff.airline_name from airline_staff where airline_staff.username=%s)=ticket.airline_name
			and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)
			group by purchases.customer_email
			order by cnt DESC"""
	cursor.execute(query , (session['username'],))
	customers=cursor.fetchall()
	return render_template('VFC.html',cus=customers,identity=session['identity'])

@app.route('/VR', methods=['GET','POST'])#view reports
def VR():
	if session['identity']!='s':
		return render_template('error.html')
	start=request.form['start']
	end=request.form['end']
	cursor=conn.cursor()
	query="""select purchases.purchase_date
			from purchases inner join ticket on purchases.ticket_id=ticket.ticket_id
			where ticket.airline_name=(select airline_name from airline_staff where airline_staff.username=%s)"""
	cursor=conn.cursor()
	query1=query+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 MONTH)"
	cursor.execute(query1 , (session['username'],))
	out1=cursor.fetchall()
	cursor=conn.cursor()
	query2=query+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)"
	cursor.execute(query2 , (session['username'],))
	out2=cursor.fetchall()
	data=list()
	if start!='' or end!='':
		cursor=conn.cursor()
		cursor.execute(query , (session['username'],))
		data=cursor.fetchall()
		if start!='':
			query3=query
			query3+=" and purchases.purchase_date >= %s"
			cursor=conn.cursor()	
			cursor.execute(query3 , (session['username'],start))
			data1=cursor.fetchall()
			data=dif(data,data1)
		if end!='':
			query1=query
			query1 += " and purchases.purchase_date <= %s"
			cursor=conn.cursor()	
			cursor.execute(query1 , (session['username'],end))
			data1=cursor.fetchall()
			data=dif(data,data1)
	print(data)
	counter1=dict()
	for i in out2:
		counter1[str(i[0])[:7]]=counter1.get(str(i[0])[:7],0)+1
	dat=pd.DataFrame(counter1.values(),index=counter1.keys())
	bar=dat.plot(kind='bar',legend=False,xlabel='month',ylabel='tickets sold',figsize=(10,10))
	bar.figure.savefig('static/barr.png')
	if len(data)!=0:
		counter2=dict()
		for i in data:
			counter2[str(i[0])[:7]]=counter2.get(str(i[0])[:7],0)+1
			dat=pd.DataFrame(counter2.values(),index=counter2.keys())
			bar=dat.plot(kind='bar',legend=False,xlabel='month',ylabel='tickets sold',figsize=(10,10))
			bar.figure.savefig('static/bbarr.png')
	return render_template('VR.html',m=len(out1),y=len(out2),s=len(data),identity=session['identity'])

@app.route('/CoRE', methods=['GET','POST'])#comparison of revenue earned
def CoRE():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	queryc="""select sum(flight.price)
			from ((purchases inner join ticket on purchases.ticket_id=ticket.ticket_id)
			inner join flight on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num)
			where ticket.airline_name=(select airline_name from airline_staff where username=%s) and purchases.booking_agent_id is null""" 
	queryb="""select sum(flight.price)
			from ((purchases inner join ticket on purchases.ticket_id=ticket.ticket_id)
			inner join flight on flight.airline_name=ticket.airline_name and flight.flight_num=ticket.flight_num)
			where ticket.airline_name=(select airline_name from airline_staff where username=%s) and purchases.booking_agent_id is not null"""
	queryclm=queryc+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 MONTH)"
	querycly=queryc+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)"
	queryblm=queryb+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 MONTH)"
	querybly=queryb+" and purchases.purchase_date>=DATE_SUB(now(), INTERVAL 1 YEAR)"
	cursor=conn.cursor()
	cursor.execute(queryclm, (session['username'],))
	clm=cursor.fetchone()[0]
	cursor=conn.cursor()
	cursor.execute(querycly, (session['username'],))
	cly=cursor.fetchone()[0]
	cursor=conn.cursor()
	cursor.execute(queryblm, (session['username'],))
	blm=cursor.fetchone()[0]
	cursor=conn.cursor()
	cursor.execute(querybly, (session['username'],))
	bly=cursor.fetchone()[0]
	dat=pd.DataFrame({'earned':[float(clm),float(blm)]},index=['cus','bok'])
	pie1=dat.plot(kind='pie',y='earned')
	pie1.figure.savefig('static/pie.png')
	dat=pd.DataFrame({'earned':[float(cly),float(bly)]},index=['cus','bok'])
	pie1=dat.plot(kind='pie',y='earned')
	pie1.figure.savefig('static/piee.png')
	return render_template('CoRE.html',identity=session['identity'])

@app.route('/VTD', methods=['GET','POST'])#view top destination
def VTD():
	if session['identity']!='s':
		return render_template('error.html')
	cursor=conn.cursor()
	querym="""select count(airport.airport_city),airport_city
			from flight inner join airport on flight.arrival_airport=airport.airport_name
            where flight.airline_name=(select airline_name from airline_staff where username=%s) and flight.arrival_time>=DATE_SUB(now(), INTERVAL 1 MONTH) and flight.departure_time<=now()
            group by airport_city
            order by count(airport_city) DESC limit 3""" 
	queryy="""select count(airport.airport_city) as cnt,airport.airport_city
			from flight inner join airport on flight.arrival_airport=airport.airport_name
			where flight.airline_name=(select airline_name from airline_staff where username=%s) and flight.arrival_time>=DATE_SUB(now(), INTERVAL 1 YEAR) and flight.departure_time<=now()
			group by airport.airport_city
			order by count(airport_city) DESC limit 3"""
	cursor.execute(querym, (session['username'],))
	m=cursor.fetchall()
	cursor=conn.cursor()
	cursor.execute(queryy, (session['username'],))
	y=cursor.fetchall()
	return render_template('VTD.html',m=m,y=y,identity=session['identity'])

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = False)
