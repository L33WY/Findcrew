from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector, bcrypt

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
    return render_template('home.html')

######## Login page ########

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in') == True:
        return redirect(url_for('user', nickname=session['nickname'])) 
    else:
        if request.method == 'POST':
            email_input = request.form['email']
            password_input = request.form['password']

            #datebase validation
            try:
                cursor = mydb.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE email = '%s'" % (email_input))
                result = cursor.fetchone()
                cursor.close()
                
                #Able to login
                if bcrypt.checkpw(password_input.encode('utf8'), result['password']):
                    session['loggedIn'] = True
                    session['nickname'] = result['nickname']
                    session['email'] = result['email']

                    return redirect(url_for('user', nickname=session['nickname']))
                #Unable to login
                else:
                    del result[:]
                    return render_template('login.html')
                    
                
            except Exception as error:
                #Dev info
                print(error)
        
        else:
            return render_template('login.html')


######### Registration page ###########

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    return render_template('registration.html')



######### User page #############

@app.route('/user/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    return render_template('user.html')

if __name__ == "__main__":
    app.run(debug=True)
