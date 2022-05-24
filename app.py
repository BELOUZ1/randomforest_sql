import pickle
from datetime import date

import numpy as np
import pandas as pd
from flask import Flask, render_template, request, session
import sys
import requests, json
import csv
import pymsgbox
import sqlite3
from flask import Flask, redirect, render_template, request

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

# Load the Random Forest CLassifier model
filename = 'diabetes-prediction-rfc-model.pkl'
classifier = pickle.load(open(filename, 'rb'))

conn = sqlite3.connect("res.sqlite")
cursor = conn.cursor()

sql_query = """ create table if not exists historique(
user text not null,
secret text not null,
glucose text not null,
insuline text not null,
pred float
)"""
cursor.execute(sql_query)

sql_query = """ create table if not exists info(
glucose text not null,
insulin text not null,
pred float
)"""
cursor.execute(sql_query)

historique_query = """  
CREATE TABLE IF NOT EXISTS historique(
id INTEGER PRIMARY KEY,
username TEXT,
password TEXT,
pregnancies TEXT,
glucose TEXT,
bloodpressure TEXT,
skinthickness TEXT,
insulin TEXT,
bmi TEXT,
dpf TEXT,
age TEXT,
pdate TEXT
)
"""

cursor.execute(historique_query)


def get_connection():
    connection = sqlite3.connect('res.sqlite')
    return connection


def add_to_history(username, password, pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, dpf, age):
    today = date.today()
    df = today.strftime("%d/%m/%Y")
    connection = get_connection()
    myCursor = connection.cursor()
    query = """
	INSERT INTO historique (
	username, password, pregnancies, 
	glucose, bloodpressure, skinthickness, 
	insulin, bmi,dpf,age, pdate)
	VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	"""
    myCursor.execute(query,
                     (username, password, pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, dpf, age,
                      df))
    connection.commit()
    connection.close()


@app.route('/')
def home():
    return render_template('log.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        preg = int(request.form['pregnancies'])
        glucose = int(request.form['glucose'])
        bp = int(request.form['bloodpressure'])
        st = int(request.form['skinthickness'])
        insulin = int(request.form['insulin'])
        bmi = float(request.form['bmi'])
        dpf = float(request.form['dpf'])
        age = int(request.form['age'])

        data = np.array([[preg, glucose, bp, st, insulin, bmi, dpf, age]])
        my_prediction = classifier.predict(data)

        username = session['username']

        add_to_history(username, "", preg, glucose, bp, st, insulin, bmi, dpf, age)
    return render_template('result.html', prediction=my_prediction)


@app.route('/sign_up', methods=['POST'])
def sign_up():
    if request.method == 'POST':
        return render_template('sign.html')


@app.route('/submite', methods=['POST'])
def submite():
    dbSubmite = get_connection()
    submiteCursor = dbSubmite.cursor()
    submiteCursor.execute("INSERT INTO user (user, secret) VALUES (?,?)",
                          (request.form['nomutil'], request.form['motpasse']))
    dbSubmite.commit()
    dbSubmite.close()
    return render_template('index.html')


@app.route('/history', methods=['GET'])
def get_all_history():
    reddit_data = []
    dbHistory = get_connection()
    historyCursor = dbHistory.cursor()

    username = session['username']

    result = historyCursor.execute("SELECT * FROM historique where username = ?", username)

    for row in result:
        element = {"id": row[0], "pregnancies": row[3],
                   "glucose": row[4], "bloodpressure": row[5], "skinthickness": row[6],
                   "insulin": row[7], "bmi": row[8], "dpf": row[9], "age": row[10]
                   }
        reddit_data.append(element)
    # return render_template('history.html', result)

    dbHistory.close()
    return render_template("show_reddit.html", data=reddit_data)


@app.route('/se_connecter', methods=['POST'])
def se_connecter():
    dbConnecter = get_connection()
    connecterCursor = dbConnecter.cursor()

    username = request.form['nomutil1']
    motdepasse = request.form['motpasse1']

    connecterCursor.execute("SELECT * FROM user WHERE user=? AND secret=?",
                            (username, motdepasse))
    result = connecterCursor.fetchall()
    dbConnecter.close()
    if len(result) == 0:
        return 'username / password not recognised'
    else:
        session['username'] = username
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
