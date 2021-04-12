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

            session['nickname'] = result['nickname']
            session['email'] = result['email']


            return redirect(url_for('user', nickname=session['nickname']))
            
        except Exception as error:
            #Dev info
            print(error)
    
    else:
        return render_template('login.html')


######### Registration page ###########

@app.route('/registration')
def registration():
    return render_template('registration.html')



######### User page #############

@app.route('/user/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    return render_template('user.html')

if __name__ == "__main__":
    app.run(debug=True)
