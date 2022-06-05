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

sql_query = """ create table if not exists user(
id INTEGER PRIMARY KEY,
nom TEXT,
prenom TEXT,
username TEXT UNIQUE,
password TEXT,
age INTEGER
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


@app.route('/predict', methods=['POST', 'GET'])
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
    else:
        nom = session.get('nom')
        prenom = session.get('prenom')
        if nom is None:
            return redirect('/')
        return render_template('index.html', message= prenom + " " + nom)


@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('sign.html')



@app.route('/submite', methods=['POST'])
def submite():
    dbSubmite = get_connection()
    submiteCursor = dbSubmite.cursor()

    nom = request.form['familyname']
    prenom = request.form['firstname']
    username = request.form['nomutil']
    password = request.form['motpasse']
    age = request.form['age']

    submiteCursor.execute("INSERT INTO user (nom, prenom, username, password, age) VALUES (?, ?, ?, ?, ?)",
                          (nom, prenom, username, password, age))
    dbSubmite.commit()
    dbSubmite.close()
    return redirect('/')


@app.route('/history', methods=['GET'])
def get_all_history():
    reddit_data = []
    dbHistory = get_connection()
    historyCursor = dbHistory.cursor()

    username = session['username']

    result = historyCursor.execute("SELECT * FROM historique where username = ?", (username,))

    for row in result:
        element = {"id": row[0], "pregnancies": row[3],
                   "glucose": row[4], "bloodpressure": row[5], "skinthickness": row[6],
                   "insulin": row[7], "bmi": row[8], "dpf": row[9], "age": row[10]
                   }
        reddit_data.append(element)
    # return render_template('history.html', result)

    dbHistory.close()
    nom = session.get('nom')
    prenom = session.get('prenom')
    return render_template("history.html", data=reddit_data, message= prenom + " " + nom)


@app.route('/se_connecter', methods=['POST'])
def se_connecter():
    dbConnecter = get_connection()
    connecterCursor = dbConnecter.cursor()

    username = request.form['nomutil1']
    motdepasse = request.form['motpasse1']

    connecterCursor.execute("SELECT * FROM user WHERE username=? AND password=?",
                            (username, motdepasse))
    result = connecterCursor.fetchall()
    dbConnecter.close()
    if len(result) == 0:
        return 'username / password not recognised'
    else:
        for element in result:
            session['nom'] = element[1]
            session['prenom'] = element[2]
            session['username'] = element[3]
        return redirect('/predict')


@app.route('/logout', methods=['GET'])
def log_out():
    session.pop('username', default=None)
    session.pop('prenom', default=None)
    session.pop('nom', default=None)
    return redirect('/')

@app.route('/statistical', methods=['GET'])
def show_stat():
    """
    cpt = 0
    cpt_pos = 0
    cpt_neg = 0
    dbHistory = get_connection()
    staticticalCursor = dbHistory.cursor()
    res = staticticalCursor.execute("SELECT * FROM historique")
    for row in res:
        cpt = cpt + 1
        if row[12] == 1:
            cpt_pos = cpt_pos + 1
        else:
            cpt_neg = cpt_neg + 1

    names = ['user', 'user positif', 'user negatif']  # nom des barres

    values = [cpt, cpt_pos, cpt_neg]
"""
    values = [40, 24, 16]
    return render_template('statis.html', income_category=json.dumps(values))

if __name__ == '__main__':
    app.run(debug=True)
