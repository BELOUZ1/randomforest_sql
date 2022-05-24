import sqlite3
from datetime import date

from flask import Flask, request, render_template, session

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

conn = sqlite3.connect("res.sqlite")
cursor = conn.cursor()

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

        session['age'] = age

        add_to_history("", "", preg, glucose, bp, st, insulin, bmi, dpf, age)

        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route('/history', methods=['GET'])
def get_all_history():
    reddit_data = []
    dbHistory = get_connection()
    historyCursor = dbHistory.cursor()
    result = historyCursor.execute("SELECT * FROM historique")
    for row in result:
        element = {"id": row[0], "pregnancies": row[3],
                   "glucose": row[4], "bloodpressure": row[5], "skinthickness": row[6],
                   "insulin": row[7], "bmi": row[8], "dpf": row[9], "age": row[10]
                   }
        reddit_data.append(element)
    # return render_template('history.html', result)

    dbHistory.close()
    return render_template("show_reddit.html", data=reddit_data)



if __name__ == '__main__':
    app.run(debug=True)
