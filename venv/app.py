from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector, bcrypt
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, timedelta, timedelta


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

### My own functions ###

def clearSession(sessionToClear):
    for record in sessionToClear:
        if session.get(record):
                session.pop(record, None)


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
                    session['userID'] = result['id']

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

        #clear old session error 
        sessionToClear = ('n_error', 'e_error', 'p_error', 'tempNickname', 'tempEmail', 'tempPassword', 'tempPassword2')
        clearSession(sessionToClear)

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
                return redirect(url_for('login'))

            except Exception as e:
                #Dev info
                # print(str(e))
                return render_template('registration.html')

        else:
            return render_template('registration.html')

    else:
        #clear old session error 
        sessionToClear = ('n_error', 'e_error', 'p_error', 'tempNickname', 'tempEmail', 'tempPassword', 'tempPassword2')
        clearSession(sessionToClear)

        return render_template('registration.html')

######## end of registration page ##########

######### User page #############

@app.route('/user/<nickname>', methods=['GET', 'POST'])
def user(nickname):
    if session.get('loggedIn'):
        
        ##### Connect to db and grab all advertisement #####

        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT id, title, description, persons, location, category, date, url, owner, TIME_FORMAT(time, '%H:%i') as time FROM advertisement2 ORDER BY date")
            advertisements = cursor.fetchall()
            
            cursor.execute("SELECT player_nick, user_id, advertisement_id FROM players")
            players = cursor.fetchall()
            cursor.close()


        except Exception as e:
            #Dev info
            print(e)

        return render_template('user-home.html', advertisements=advertisements, players=players)
    else:
        return redirect(url_for('login'))

############ user-join advertisement #############
@app.route('/user/join', methods=['POST', 'GET'])
def userJoin():
    if session['loggedIn'] == True:

        if request.method == 'POST':
            
            #connect to db
            try:
                #check how many players are still to find
                advertisement_id = int(request.form['id'])
                cursor = mydb.cursor(dictionary=True)
                cursor.execute("SELECT persons FROM advertisement2 WHERE id=%s", (advertisement_id, ))
                playersToFind = cursor.fetchone()
                playersToFind = playersToFind['persons']
                
                #Check if avalible spot
                if playersToFind-1 >= 0:
                    playersToFind -= 1

                    #check if player already in advertisemnt
                    try:
                        cursor.execute("SELECT * FROM players WHERE user_id=%s AND advertisement_id=%s", (session['userID'], advertisement_id))
                        recordFound = len(cursor.fetchall())

                        if recordFound > 0:
                            return redirect(url_for('user', nickname = session['nickname']))

                        else:
                            try:
                                #assign user to advertisement and change searched playes number
                                cursor.execute("INSERT INTO players VALUES (%s, %s, %s)", (session['nickname'], session['userID'], advertisement_id))

                                cursor.execute("UPDATE advertisement2 SET persons=%s WHERE id=%s", (playersToFind, advertisement_id))
                                mydb.commit()

                            except Exception as e:
                                #dev info
                                print(e)
                                return redirect(url_for('user', nickname = session['nickname']))

                    except Exception as e:
                        #dev info 
                        print(e)
                        return redirect(url_for('user', nickname = session['nickname']))

                else:
                    return redirect(url_for('user', nickname = session['nickname']))


            except Exception as e:
                #dev info
                print(e)
                return redirect(url_for('user', nickname = session['nickname']))

            return redirect(url_for('user', nickname = session['nickname']))
    else:
        return redirect(url_for('login'))





######## user-page-create advertisement ##########
@app.route('/user/<nickname>/create-ad', methods=['GET', 'POST'])
def create_ad(nickname):
    if session.get('loggedIn'):

        ##### Creating new advertisement #####

        if request.method == 'POST':

            #clear old session
            sessionToClear = ('t_error', 'd_error', 'date_error', 'tempTitle', 'tempDescription')
            clearSession(sessionToClear)

            #fetch input data

            input_title = request.form['title']
            input_description = request.form['description']
            input_category =  request.form['category']
            input_location = request.form['location']
            input_date = request.form['date']
            input_time = request.form['time']
            input_persons = request.form['persons']

            #create temporary input
            session['tempTitle'] = input_title
            session['tempDescription'] = input_description        

            ### input data validation ###

            createAdComplete = True

            ## title validation ##
            if len(input_title) < 4 or len(input_title) > 40:
                createAdComplete = False
                session['t_error'] = "Tytuł może mieć od 4 do 40 znaków"

            if not all(char.isalnum() or char.isspace() for char in input_title):
                createAdComplete = False
                session['t_error'] = "Tytuł nie może zawierać znaków specjalnych"

            
            ## description validation
            if len(input_description) < 15 or len(input_description) > 200:
                createAdComplete = False
                session['d_error'] = "Opis może zawierać od 15 do 200 znaków"
            
            if not all(char.isalnum() or char.isspace() or char=='.' for char in input_description):
                createAdComplete = False
                session['d_error'] = "Opis nie może zawierać znaków specjalnych"


            ## date validation
            currentDate = datetime.today().strftime('%Y-%m-%d')
            currentDate = datetime.strptime(currentDate, '%Y-%m-%d')
            try:
                input_date = datetime.strptime(input_date, '%Y-%m-%d')

                if input_date < currentDate:
                    createAdComplete = False
                    session['date_error'] = "Data musi być aktualna"
                

                avalibleTime = currentDate + timedelta(days=7)

                if input_date > avalibleTime:
                    createAdComplete = False
                    session['date_error'] = "wydarzenie może być maksymalnie z tygodniowym wyprzedzeniem"
            except:
                createAdComplete = False
                session['date_error'] = "Data musi być w formacie DD/MM/YYYY"

            ## assign suitable img url
            if input_location == "Zespół Szkół Ogólnokształcących nr. 1":
                locationImgUrl = 'images/a1.jpg'
            elif input_location == "Boisko Komarowo":
                locationImgUrl = 'images/a2.jpg'
            elif input_location == "Boisko na Chicago":
                locationImgUrl = 'images/a3.jpg'
            elif input_location == "Faktoria":
                locationImgUrl = 'images/a4.jpg'
                    
            ### try add new advertisement to database ###

            if createAdComplete == True:
                try:
                    cursor = mydb.cursor(dictionary=True)
                    query = "INSERT INTO advertisement2 (title, category, description, location, time, date, persons, owner, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (input_title, input_category, input_description, input_location, input_time, input_date, input_persons, session['nickname'], locationImgUrl)
                    cursor.execute(query, values)
                    mydb.commit()
                
                except Exception as e:
                    #dev info
                    # print(e)
                    redirect(url_for('create-ad', nickname=session['nickname']))


            return render_template('user-create-ad.html')

        else:
            #clear old session
            sessionToClear = ('t_error', 'd_error', 'date_error', 'tempTitle', 'tempDescription')
            clearSession(sessionToClear)

            return render_template('user-create-ad.html')
        

        
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
