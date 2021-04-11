from flask import Flask, redirect, render_template, url_for, session, request
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('login'))

# Logowanie

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_input = request.form['email']
        password_input = request.form['password']

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
