from collections import Counter

import csv
import sqlite3
    
from flask import Flask, request, g
    
DATABASE = '/var/www/html/flaskapp/natlpark.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

@app.route("/viewdb")
def viewdb():
    rows = execute_query("SELECT * FROM natlpark")
    return '<br>'.join(str(row) for row in rows)

@app.route("/state/<state>")
def state_query(state):
    rows = execute_query("SELECT * FROM natlpark WHERE state = ?", 
                         [state.title()])
    return '<br>'.join(str(row) for row in rows)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/countme/<in_str>')
def count_me(in_str):
    return '<br>'.join('"{}": {}'.format(let, cnt)
                       for let, cnt in Counter(in_str).most_common())


if __name__ == '__main__':
    app.run()
