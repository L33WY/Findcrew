from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector, bcrypt
from email_validator import validate_email, EmailNotValidError

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
                cursor.execute("SELECT * FROM users2 WHERE email = '%s'" % (email_input))
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

    if request.method == 'POST':

        #asign form variables
        nickname_input = request.form['nickname']
        email_input = request.form['email']
        password_input = request.form['password']
        password_input2 = request.form['repeatPassword']

        ### Registration validation ###
        registrationComplete = True

        #remember temporary data inputs
        session['tempNickname'] = nickname_input
        session['tempEmail'] = email_input
        session['tempPassword'] = password_input
        session['tempPassword2'] = password_input2

        #nickname validation
        if len(nickname_input) < 4 or len(nickname_input) > 20:
            registrationComplete = False
            session['n_error'] = "Nick musi zawierać od 4 do 20 znaków !" 

        if not nickname_input.isalnum():
            registrationComplete = False
            session['n_error'] = "Nick nie może zaiwerać znaków specjalnych !"

        #email validation
        try:
            email_valid = validate_email(email_input)
            email = email_valid.email
        except EmailNotValidError as e:
            #dev info
            # print(str(e))
            registrationComplete = False
            session['e_error'] = "Podaj poprawny email !"

        #password validation
        if len(password_input) < 6 or len(password_input) > 20:
            registrationComplete = False
            session['p_error'] = "Hasło musi zawierać od 6 do 20 znaków !"
        
        if not password_input.isalnum():
            registrationComplete = False
            session['p_error'] = "Hasło nie może zaiwerać znaków specjalnych !"
        
        if password_input != password_input2:
            registrationComplete = False
            session['p_error'] = "Hasła muszą być identyczne !"

        ### validation with database ###

        # is nick name avalible?
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT nickname FROM users2 WHERE nickname = '%s'" % (nickname_input))
        record = cursor.fetchall()      

        if len(record) > 0:
            registrationComplete = False
            session['n_error'] = "Nickname jest już zajęty!"
        
        #is Email avalible? 
        cursor.execute("SELECT email FROM users2 WHERE email = '%s'" % (email_input))
        record = cursor.fetchall()

        if len(record) > 0:
            registrationComplete = False
            session['e_error'] = "Email jest już zajęty!"
        
        ###is Validation success? ###
        if registrationComplete:

            hashed_password = bcrypt.hashpw(password_input.encode('utf8'), bcrypt.gensalt())

            try:
                cursor = mydb.cursor(dictionary=True)
                query = "INSERT INTO users2 (password, nickname, email) VALUES (%s, %s, %s)"
                values = (hashed_password, nickname_input, email_input)
                cursor.execute(query, values)
                mydb.commit()
                session['loggedIn'] = True
                session['nickname'] = nickname_input
                session['email'] = email_input
                return redirect(url_for('user', nickname=nickname_input))

            except Exception as e:
                #Dev info
                # print(str(e))
                return render_template('registration.html')

        else:
            return render_template('registration.html')

    else:
        #clear old session error 
        session.pop('n_error', None)
        session.pop('e_error', None)
        session.pop('p_error', None)
        session.pop('tempNickname', None)
        session.pop('tempEmail', None)
        session.pop('tempPassword', None)
        session.pop('tempPassword2', None)

        return render_template('registration.html')

######## end of registration page ##########

######### User page #############

@app.route('/user/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    if session.get('loggedIn'):
        
        ##### Connect to db and grab all advertisement #####

        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT title, description, persons, location, category, date, url, TIME_FORMAT(time, '%H:%i') as time FROM advertisement2 ORDER BY date")
            advertisements = cursor.fetchall()
            cursor.close()

        except Exception as e:
            #Dev info
            print(e)

        return render_template('user-home.html', advertisements=advertisements)
    else:
        return redirect(url_for('login'))

######## user-page-create advertisement ##########
@app.route('/user/<nickname>/create-ad', methods=['GET', 'POST'])
def create_ad(nickname):
    if session.get('loggedIn'):
        
        ##### Creating new advertisement #####


        return render_template('user-create-ad.html')
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
