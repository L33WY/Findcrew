from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector

#Flask setup
app = Flask(__name__)
app.secret_key = "dusadhHdu13u1HE1h3H3EIjdas1pop23j"


#Database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="findcrew"
)


#################### Wirtyny ###################

#index page

@app.route('/')
def index():
    return redirect(url_for('login'))

######## Login page ########

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_input = request.form['email']
        password_input = request.form['password']

        #datebase validation
        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE password = '%s' and email = '%s'" % (password_input, email_input))
            result = cursor.fetchone()
            cursor.close()

            session['username'] = result['name']
            session['lastname'] = result['lastName']
            session['nickname'] = result['nickname']
            session['age'] = result['age']
            session['email'] = result['email']
            session['city'] = result['city']

            return render_template('user.html')
            
        except Exception as error:
            #Dev info
            print(error)
    
    else:
        return render_template('login.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    return render_template('user.html')

if __name__ == "__main__":
    app.run(debug=True)
