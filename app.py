
from flask import Flask, render_template, request, session, redirect

from flask_mysqldb import MySQL


from flask_session import Session

app = Flask(__name__)
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
    return render_template('trek.html', result={"trek": trek, "logged_in_user": logged_in_user})


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

    print(trekId)
    print(title)
    print(days)
    print(startPlace)
    print(endPlace)
    print(description)
    print(duration)
    print(cost)




    cursor = mysql.connection.cursor()
    cursor.execute('''INSERT INTO iternaries VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)''',
                   (title, days, startPlace, endPlace, description, duration, cost, trekId))
    mysql.connection.commit()
    cursor.close()

    return redirect('/treks')


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


if __name__ == '__main__':
    app.run(debug=True)
