from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)
app.secret_key = "dusadhHdu13u1HE1h3H3EIjdas1pop23j"

#Database

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="findcrew"
)


@app.route('/')
def index():
    return redirect(url_for('login'))

# Logowanie

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_input = request.form['email']
        password_input = request.form['password']

        #datebase validation
        conn = mydb.cursor()
        try:
            conn.execute("SELECT * FROM users WHERE password = '%s' and email = '%s'" % (password_input, email_input))
            result = conn.fetchall()

            session['username'] = result[0][2]
            print("##############################")
            print(session['username'])
            session['lastname'] = result[0][3]
            session['nickname'] = result[0][5]
            session['age'] = result[0][6]
            session['email'] = result[0][7]
            session['city'] = result[0][8]

            return redirect(url_for('user'))
        except:
            return "Cos poszlo nie tak"
    

    return render_template('login.html')

@app.route('/user')
def user():
    return render_template('user.html')

if __name__ == "__main__":
    app.run(debug=True)
