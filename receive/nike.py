from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)


@app.route('/')
def orders():
    db = pymysql.connect(host="localhost", user="root",
                         password="admin123", database="nike")
                         
    cur = db.cursor()

    cur.execute('SELECT * FROM orders')

    data = cur.fetchall()

    return render_template('home.html', data=data)


if __name__ == "__main__":
    app.run(host='localhost', port=3000, debug=True)
