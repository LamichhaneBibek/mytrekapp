# impotring Flask

import uuid
from flask import Flask, render_template, request, session, redirect,jsonify
# for database
from flask_mysqldb import MySQL
# for session
from flask_session import Session
# initializing app
app = Flask(__name__)

# for unique id

# database settings for mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_trekapp'

# session settings
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mysql = MySQL(app)


@app.route('/')
def index():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    return render_template("index.html", result={'logged_in_user': logged_in_user})


# @app.route('/home')
# def home():
#     logged_in_user = None
#     if session.get("email"):
#         logged_in_user = session["email"]

#     return render_template("home.html",result=logged_in_user)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/doLogin', methods=['POST'])
def doLogin():
    email = request.form['email']
    password = request.form['psw']

    cursor = mysql.connection.cursor()
    resp = cursor.execute(
        '''SELECT id, email, fullName, password FROM users WHERE email=%s and password=%s;''', (email, password))
    user = cursor.fetchone()
    cursor.close()

    if resp == 1:
        session['email'] = email
        session['userId'] = user[0]
        logged_in_user = session.get('email')
        return render_template('home.html', result={'logged_in_user': logged_in_user})
    else:
        return render_template('login.html', result="Invalid Credentials")


@app.route('/doRegister', methods=['POST'])
def doRegister():
    fullName = request.form['fullName']
    email = request.form['email']
    cNumber = request.form['cNumber']
    address = request.form['address']
    password = request.form['password']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO users VALUES(NULL,%s,%s,%s,%s,%s)''',
                   (fullName, email, cNumber, address, password))
    mysql.connection.commit()
    cursor.close()

    return render_template('login.html', result="Registered Successfully")


@app.route('/treks')
def treks():

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.des_id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.totalCost as 'Total Cost', td.upVotes as 'Upvotes', u.fullName as 'Full Name' FROM trekDestinations as td join users as u on td.userId = u.id;''')
    trek = cursor.fetchall()
    cursor.close()

    logged_in_user = None
    if session.get("email"):
        logged_in_user = session['email']

    if session.get('userId'):
        userId = session.get('userId')
    return render_template('trek.html', result={"trek": trek, "logged_in_user": logged_in_user, "userId": userId})


@app.route('/trek/<int:trekID>')
def getTrekbyId(trekID):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.des_id as 'SNO', td.title as 'Title', td.days as 'Days', td.difficulty as 'Difficulty', td.totalCost as 'Total Cost', td.upVotes as 'Upvotes', u.fullName as 'Full Name' FROM trekDestinations as td join users as u on td.userId = u.id where td.des_id = %s;''', (trekID,))
    trek = cursor.fetchone()
    cursor.close()

    cursor = mysql.connection.cursor()
    cursor.execute(
        '''SELECT * FROM iternaries WHERE trekId = %s;''', (trekID,))
    iternaries = cursor.fetchall()

    cursor.close()

    return render_template('trekDetails.html', result={"trek": trek, "iternaries": iternaries})


@app.route('/doUpdateTrek', methods=['POST'])
def doUpdateTrek():
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]

    title = request.form['title']
    days = request.form['days']
    difficulty = request.form['difficulty']
    totalCost = request.form['totalCost']
    trekId = request.form['trekId']

    cursor = mysql.connection.cursor()
    cursor.execute('''UPDATE `trekDestinations` SET `title` = %s,`days`=%s,`difficulty`=%s,`totalCost`=%s WHERE `des_id` = %s;''',(title,days,difficulty,totalCost,trekId))
    mysql.connection.commit()
    cursor.close()

    return redirect('/treks')

@app.route('/doDeleteTrek/<int:trekId>')
def doDeleteTrek(trekId):
    cursor = mysql.connection.cursor()
    cursor.execute('''DELETE FROM `trekDestinations` WHERE `des_id` = %s;''',(trekId,))
    mysql.connection.commit()
    cursor.close()

    return redirect('/treks')


@app.route('/logout')
def logout():
    session["email"] = None
    session["userId"] = None
    return redirect('/')


@app.route('/addTrek')
def addTrek():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    return render_template('addtrek.html', result={'logged_in_user': logged_in_user})


@app.route('/doAddTrek', methods=['POST'])
def doAddTrek():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    title = request.form['title']
    days = request.form['days']
    difficulty = request.form['difficulty']
    totalcost = request.form['totalCost']
    upvotes = 0

    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT id from users where email = %s;''',
                   (logged_in_user,))
    user = cursor.fetchone()
    cursor.close()
    userId = user[0]

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO trekDestinations VALUES(NULL,%s,%s,%s,%s,%s,%s)''',
                   (title, days, difficulty, totalcost, upvotes, userId))
    mysql.connection.commit()
    cursor.close()

    return redirect('/treks')


@app.route('/addIternary')
def addIternary():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    cursor = mysql.connection.cursor()
    userId = None
    if session.get('userId'):
        userId = session.get('userId')
    cursor.execute(
        '''SELECT des_id,title FROM trekDestinations WHERE userId = %s;''', (userId,))
    treks = cursor.fetchall()
    cursor.close()

    return render_template('addIternary.html', result={'treks': treks, 'logged_in_user': logged_in_user})


@app.route('/editTrek/<int:trekId>')
def editTrek(trekId):
    logged_in_user = None
    if session.get('email'):
        logged_in_user = session["email"]
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT td.des_id as 'SNO',td.title as 'Title',td.days as 'Days',td.difficulty as 'Difficulty',td.totalCost as 'Total Cost',td.upVotes as 'Upvotes',u.fullName as 'Full Name' FROM `trekDestinations` as td join `users` as u on td.userId = u.id WHERE td.des_id=%s;''', (trekId,))
    trek = cursor.fetchone()
    cursor.close()

    return render_template('editTrek.html', result={"trek": trek, "logged_in_user": logged_in_user})


@app.route('/doAddIternary', methods=['POST'])
def doAddIternary():
    logged_in_user = None
    if session.get("email"):
        logged_in_user = session["email"]

    trekId = request.form['trekId']
    title = request.form['title']
    days = request.form['days']
    startPlace = request.form['startPlace']
    endPlace = request.form['endPlace']
    description = request.form['description']
    duration = request.form['duration']
    cost = request.form['cost']

    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO iternaries VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)''',
                   (title, days, startPlace, endPlace, description, duration, cost, trekId))
    mysql.connection.commit()
    cursor.close()

    return redirect('/addIternary')


def __getUserIdByEmail(email):

    pass


@app.route('/iternary/<int:trekId>')
def getIternarybyTrekId(trekId):

    cursor = mysql.connection.cursor()
    cursor.execute(
        '''SELECT * FROM iternaries WHERE trekId = %s;''', (trekId,))
    iternaries = cursor.fetchall()

    cursor.close()

    return render_template('iternary.html', result={"trekId": trekId, "iternaries": iternaries})


@app.route('/myTreks/<string:param>')
def getTreksbyUser(param):
	userId=None
	if session.get('email'):
		logged_in_user=session["email"]

	if session.get('userId'):
		userId=session.get('userId')

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	if param == "user":
		cursor.execute('''SELECT * FROM trekDestinations WHERE userId=%s;''',(userId,)) 
	else:
		cursor.execute('''SELECT * FROM trekDestinations;''') 
	treks = cursor.fetchall()
	print(userId)
	cursor.close()

	return render_template('myTrek.html',result={"treks":treks,"userId":userId})

# """
# APT Interfaces defined from here
# """

@app.route('/api/doRegister',methods=['POST'])
def doRegisterAPI():
	
	full_name=request.json['full_name']
	email=request.json['email']
	phone_number=request.json['phone_number']
	address=request.json['address']
	password=request.json['psw']

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO users VALUES(NULL,%s,%s,%s,%s,%s);''',(full_name,address,email,phone_number,password))
	mysql.connection.commit()
	cursor.close()
	#return render_template('login.html',result="Register Successfull!! Please Login To Continue.....")
	return jsonify({"result":"Register Successfull!! Please Login To Continue....."})

# @app.route('/api/treks')
@app.route('/rest/treks')
def allTreksAPI():

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	cursor.execute('''SELECT td.id as 'SNO',td.title as 'Title',td.day as 'Days',td.difficulty as 'Difficulty',td.totalCost as 'Total Cost',td.upVotes as 'Upvotes',u.fullName as 'Full Name' FROM `trekDestination` as td join `users` as u on td.trekId = u.id;''')
	treks = cursor.fetchall()
	# print(treks)
	cursor.close()

	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]
	
	result={"treks":treks,"logged_in_user":logged_in_user}
	#return render_template('listing.html',result={"treks":treks,"logged_in_user":logged_in_user})
	return jsonify(result)


@app.route('/api/doLogin',methods=['POST'])
def doLoginAPI():
	email =request.json['email']
	password=request.json['psw']

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	#resp=cursor.execute('''SELECT * FROM user WHERE email=%s and password=%s;''',(email,password))
	resp=cursor.execute('''SELECT id,email,fullName,pass FROM user WHERE email=%s and pass=%s;''',(email,password))
		
	user=cursor.fetchone()
	print(user)
	cursor.close()

	token=""
	if resp==1: #if email and password exist in the Database then It would lets you to  Login and return value 1 in the Variable Resp
		session['email']=email  
		session['userId']= user[0]
		logged_in_user=session.get('email')
		token=str(uuid.uuid4())

		cursor = mysql.connection.cursor()
		cursor.execute('''UPDATE users SET `token`=%s WHERE `email`=%s;''',(token,email))
		mysql.connection.commit()
		cursor.close()

		return jsonify({"message":"Login Successfull!!","loggedin":True,"token":token})
	else:
		return jsonify({"message":"Login Unsuccessfull!! Check your email and password","loggedin":False})

# @app.route('/api/doAddTrek',methods=['POST'])
@app.route('/rest/treks',methods=['POST'])
def doAddTrekAPI():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	title=request.json['title']
	days=request.json['days']
	difficulty=request.json['difficulty']
	total_cost=request.json['total_cost']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})
	upvotes=0

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO trekDestination VALUES(NULL,%s,%s,%s,%s,%s,%s);''',(title,days,difficulty,total_cost,upvotes,userID))
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been added successfully!!"})

# @app.route('/api/doUpdateTrek',methods=['PUT'])
@app.route('/rest/treks',methods=['PUT'])
def doUpdateTrekAPI():
	title=request.json['title']
	days=request.json['days']
	difficulty=request.json['difficulty']
	total_cost=request.json['total_cost']
	trekId=request.json['trekId']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})

	cursor = mysql.connection.cursor()
	cursor.execute('''UPDATE `trekDestination` SET `title` = %s,`day`=%s,`difficulty`=%s,`totalCost`=%s WHERE `id` = %s;''',(title,days,difficulty,total_cost,trekId))
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been updated successfully!!"})

# @app.route('/api/doDeleteTrek',methods=['DELETE'])
@app.route('/rest/treks',methods=['DELETE'])
def doDeleteTrekAPI():

	trekId=request.json['trekId']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})

	cursor = mysql.connection.cursor()
	resp=cursor.execute('''DELETE FRoM `trekDestination` WHERE `id` = %s and `trekId`=%s;''',(trekId,userID))
	if resp==0:
		return jsonify({"message":"You Cannot Delete someone else Trek!!"})
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been deleted successfully!!"})
	

def __validate_token(token):
	cursor = mysql.connection.cursor()
	cursor.execute('''SELECT id FROM `users` WHERE `token`=%s;''',(token,))
	user = cursor.fetchone()
	cursor.close()
	userID = 0
	if user is not None:
		userID=user[0]

	return userID





if __name__ == '__main__':
    app.run(debug=True)
