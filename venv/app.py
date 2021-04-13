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
    if session.get('loggedIn'):
        return redirect(url_for('user', nickname=session['nickname'])) 
    else:
        session.pop('error', None)
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
                    session['error'] = "Bledny email lub haslo !"
                    return render_template('login.html')
                    
                
            except Exception as error:
                #Dev info
                # print(error)
                session['error'] = "Bledny email lub haslo !"
                return render_template('login.html')
        
        else:
            return render_template('login.html')

###### logout page ######
@app.route('/logout')
def logout():
    for record in list(session.keys()):
        session.pop(record)
    return redirect(url_for('index'))


######### Registration page ###########

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    #clear old session error 
    session.pop('n_error', None)


    if request.method == 'POST':

        #asign form variables
        nickname_input = request.form['nickname']
        email_input = request.form['email']
        password_input = request.form['password']
        password_input2 = request.form['password']

        ### Registration validation ###
        registrationComplete = True

        #nickname validation
        if len(nickname_input) < 4 or len(nickname_input) > 20:
            registrationComplete = False
            session['n_error'] = "Nick musi zawierać od 4 do 20 znaków !" 

        if not nickname_input.isalpha():
            registrationComplete = False
            session['n_error'] = "Nick nie może zaiwerać znaków specjalnych !"

        #email validation
        #??????????



        return render_template('registration.html')

    else:
        return render_template('registration.html')



######### User page #############

@app.route('/user/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    if session.get('loggedIn'):
        return render_template('user.html')
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
