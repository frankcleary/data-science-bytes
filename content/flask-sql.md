Title: Using Flask to answer SQL queries
Date: 2-28-2015
Category: Tutorials
Tags: python, AWS, SQL

##### _Four Part series on creating a D3.js graph powered by Flask and SQL_

1. [Running a Flask app on AWS EC2]({filename}/flask-on-ec2.md)
1. **Using Flask to answer SQL queries**
1. [Getting csv data from requests to a SQL backed Flask app]({filename}/flask-bart-sql.md)
1. [A D3.js plot powered by a SQL database]({filename}/flask-bart-graphing.md)

In an [part 1]({filename}/flask-on-ec2.md) I describe how to set up a Flask service on an AWS EC2 instance. In this post I'll set up the server to respond to queries against a SQL database.

# Creating a database

### 1. The data

We'll use [`sqlite3`](https://docs.python.org/2/library/sqlite3.html) to provide an interface from python to SQL. For this example we'll create a simple database of national parks, the data is [here](/data/nationalparks.csv), originally from [wikipedia](http://en.wikipedia.org/wiki/List_of_areas_in_the_United_States_National_Park_System#National_parks).

A look at the data:

    :::console
    $ head nationalparks.csv
    Name,Location,Year Established,Area
    Acadia National Park,Maine,1919,48876.58
    National Park of American Samoa,American Samoa,1988,8256.67
    Arches National Park,Utah,1971,76678.98
    Badlands National Park,South Dakota,1978,242755.94

### 2. Creating the database

This script populates a database with the data from the file:

    :::python
    import csv
    import sqlite3

    conn = sqlite3.connect('natlpark.db')
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS natlpark""")
    cur.execute("""CREATE TABLE natlpark
                (name text, state text, year integer, area float)""")

    with open('nationalparks.csv', 'r') as f:
        reader = csv.reader(f.readlines()[1:])  # exclude header line
        cur.executemany("""INSERT INTO natlpark VALUES (?,?,?,?)""",
                        (row for row in reader))
    conn.commit()
    conn.close()

### 3. Accessing the database from Flask

Add the following lines to `flaskapp.py` (see [earlier post]({filename}/flask-on-ec2.md)). This code handles correctly managing connections to the database and provides a convenient query method.

    :::python
    import csv
    import sqlite3

    from flask import Flask, request, g

    DATABASE = '/var/www/html/flaskapp/natlpark.db'

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

### 4. Add a request handler to show the database

Add the following to `flaskapp.py` and restart the server (`sudo apachectl restart`). Pointing a browser at `(your public DNS)/viewdb` should show the entire database.

    :::python
    @app.route("/viewdb")sf
    def viewdb():
        rows = execute_query("SELECT * FROM natlpark")
        return '<br>'.join(str(row) for row in rows)

<img src="/extra/images/flasksql/viewdb.png" title="View SQL with flask">

### 5. Add a query url request handler

To allow for queries on state, add the following to `flaskapp.py` and restart the server (`sudo apachectl restart`). Pointing a browser at `(your public DNS)/state/(field)` will return a list of all national parks in that state.

    :::python
    @app.route("/state/<state>")
    def sortby(state):
        rows = execute_query("SELECT * FROM natlpark WHERE state = ?",
                             [state.title()])
        return '<br>'.join(str(row) for row in rows)

<img src="/extra/images/flasksql/statequery.png" title="Query SQL with flask">

### 6. Note on cross site requests

##### _Four Part series on creating a D3.js graph powered by Flask and SQL_

1. [Running a Flask app on AWS EC2]({filename}/flask-on-ec2.md)
1. **Using Flask to answer SQL queries**
1. [Getting csv data from requests to a SQL backed Flask app]({filename}/flask-bart-sql.md)
1. [A D3.js plot powered by a SQL database]({filename}/flask-bart-graphing.md)
