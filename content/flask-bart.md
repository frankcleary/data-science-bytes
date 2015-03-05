Title: Using Flask to power a D3.js plot with a SQL database
Date: 3-3-2015
Category: Tutorials
Tags: python, AWS, SQL

In this post I'll describe a simple flask app that receives requests from a D3.js plotting script  and returns csv format data from a SQL database. See [Part 1 - Running a Flask app on AWS EC2]({filename}/flask-on-ec2.md) and [Part 2 -  Using Flask to answer SQL queries]({filename}/flask-sql.md) for background information.

# The data

<img src="/extra/images/flaskbart/graph.png" title="Bart data graph">

This is what the end result looks like on the front end. Any selection for what data to graph gets sent to the Flask server and the selected data is returned from the SQL database.

The data is acquired from the [BART API](http://api.bart.gov/), after a bit of xml parsing I create csv files with data about the each train's ETD, destination, etc (see [`plza.csv`](/data/plza.csv), [related post]({filename}/bart-reshape-plot.ipynb)).

    :::console
    $ head -n5 plza.csv
    time,dest,dir,len,etd
    1417108837.85,Fremont,South,6,3
    1417108837.85,Richmond,North,6,10
    1417108921.12,Fremont,South,6,2
    1417108921.12,Richmond,North,6,9
