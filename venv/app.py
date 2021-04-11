from flask import Flask, redirect, render_template, url_for
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)