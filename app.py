"""from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import subprocess
import os
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('index.html', selected_date=selected_date, no_data=True)
    
    return render_template('index.html', selected_date=selected_date, attendance_data=attendance_data)

@app.route('/take_attendance', methods=['GET', 'POST'])
def take_attendance():
    if request.method == 'POST':
        # Perform the attendance-taking process (e.g., execute attendance_taker.py)
        subprocess.run(['python', 'D:\Attendance\Face-Recognition-Based-Attendance-System-main\Attendance_taker.py'])
        return redirect(url_for('index'))
    
    return render_template('take_attendance.html')

if __name__ == '__main__':
    app.run(debug=True)
"""
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import subprocess
import os
import pandas as pd
import re
import mysql.connector

app = Flask(__name__)
app.secret_key = 'xyzsdfg'  # Same secret key as in the login system

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Abhinaya@2004'
app.config['MYSQL_DB'] = 'abhi'

mysql = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

# Removed the global cursor object
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/view')
def view():
    return render_template('view.html')

@app.route('/Attend')
def Attend():
    return render_template('Attend.html')


@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', selected_date='', no_data=False)
    else:
        return redirect(url_for('login_page'))
    

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        # Creating cursor within a with statement
        with mysql.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            if user:
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                message = 'Logged in successfully !'
                return redirect(url_for('index'))
            else:
                message = 'Please enter correct email / password !'
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        # Creating cursor within a with statement
        with mysql.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                message = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Invalid email address !'
            elif not userName or not password or not email:
                message = 'Please fill out the form !'
            else:
                cursor.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (userName, email, password))
                mysql.commit()  # Commit directly on the connection object
                message = 'You have successfully registered !'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('register.html', message=message)

@app.route('/attendance', methods=['POST'])
def attendance():
    selected_date = request.form.get('selected_date')
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
    formatted_date = selected_date_obj.strftime('%Y-%m-%d')

    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
    attendance_data = cursor.fetchall()

    conn.close()

    if not attendance_data:
        return render_template('view.html', selected_date=selected_date, no_data=True)

    return render_template('view.html', selected_date=selected_date, attendance_data=attendance_data)


@app.route('/take_attendance', methods=['GET', 'POST'])
def take_attendance():
    if 'loggedin' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        # Perform the attendance-taking process (e.g., execute attendance_taker.py)
        subprocess.run(['python', 'D:\Attendance\Face-Recognition-Based-Attendance-System-main\Attendance_taker.py'])
        return redirect(url_for('Attend'))
    return render_template('take_attendance.html')


@app.route('/remove_attendance', methods=['GET', 'POST'])
def remove_attendance():
    if 'loggedin' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        # Perform the attendance-taking process (e.g., execute attendance_taker.py)
        subprocess.run(['python', 'D:\Attendance\Face-Recognition-Based-Attendance-System-main\Attendance_remover.py'])
        return redirect(url_for('Attend'))

    return render_template('remove_attendance.html')

if __name__ == '__main__':
    app.run(debug=True)
