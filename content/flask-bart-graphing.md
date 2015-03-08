Title: A D3.js plot powered by a SQL database
Date: 3-7-2015
Category: Tutorials
Tags: python, AWS, SQL, D3

##### _Four Part series on creating a D3.js graph powered by Flask and SQL_

1. [Running a Flask app on AWS EC2]({filename}/flask-on-ec2.md)
1. [Using Flask to answer SQL queries]({filename}/flask-sql.md)
1. [Getting csv data from requests to a SQL backed Flask app]({filename}/flask-bart-sql.md)
1. **A D3.js plot powered by a SQL database**

In [Part 3]({filename}/flask-bart-sql.md) of this tutorial I covered setting up a SQL database queryable via an endpoint provided by Flask. Here in Part 4 I'll go over the actual D3.js code to visualize the data and update the graph based on user input. One of the great things about this architecture is that the static content (html, css and javascript) can be hosted just about anywhere and is decoupled from the backend resource that provides the data (in this case a Flask site running on EC2). By using a DNS to point to the backend, you're free to change the the backend however you like, scaling as usage scales, without altering the visualization code.

The end result is shown below - play around with the selection boxes to see the data change (note that some combinations of station, day and destination will not produce any data). One of the original motivations for this project was to answer the question "What is the latest I can leave work while still having a 90% probability of making my intended train?"

# End result

<iframe src="http://aws.datasciencebytes.com/bartdb/static/graph.html" width="700px" height="600px"></iframe>

# Javascript source

Here is the code that generates the plot using D3.js.

    :::js
    // The base endpoint to receive data from. See update_url()
    var URL_BASE = "http://aws.datasciencebytes.com/bartdb";

    // Update graph in response to inputs
    d3.select("#dest").on("input", make_graph);
    d3.select("#day_select").on("input", make_graph);
    d3.select("#station_select").on("input", make_graph);
    d3.select("#day_select").on("input", make_graph);
    d3.select("#time").on("input", make_graph);

    var margin = {top: 20, right: 20, bottom: 100, left: 60};
    var width = 600 - margin.left - margin.right;
    var height = 400 - margin.top - margin.bottom;

    // Whitespace on either side of the bars in units of minutes
    var binMargin = .1;

    var x = d3.scale.linear()
        .range([0,  width])
        .domain([0, 25]);
    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(6);
    var y = d3.scale.linear()
        .range([height, 0]);
    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .ticks(10);

    var svg = d3.select("body").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

    // x axis
    svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)
        .append("text")
          .text("ETD (minutes)")
          .attr("dy", "3em")
          .attr("text-align", "center")
          .attr("x", width / 2 - margin.right - margin.left);

    // y axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("dy", "-2em")
        .text("Count");

    // Update the time displayed (XX:XX) next to the time slider
    function update_slider(time) {
      var dateObj = new Date();
      dateObj.setHours(Math.floor(time/60));
      dateObj.setMinutes(time % 60);
      d3.select("#prettyTime")
        .text(dateObj.toTimeString().substring(0, 5));
    }

    // Return url to recieve csv data with query filled in from input fields
    function update_url() {
      return URL_BASE +
            "?dest=" + document.getElementById("dest").value +
            "&time=" + document.getElementById("time").value +
            "&station=" + document.getElementById("station_select").value +
            "&day=" + document.getElementById("day_select").value;
    }

    // Convert csv data to number types
    function type(d) {
      d.etd = +d.etd;
      d.count = +d.count;
      return d;
    }

    function make_graph() {
      update_slider(+document.getElementById("time").value);
      url = update_url()
      d3.csv(url, type, function(error, data) {
        y.domain([0, d3.max(data, function(d) { return d.count; })]);

        svg.selectAll("g.y.axis")
          .call(yAxis);

        var bars = svg.selectAll(".bar")
          .data(data, function(d) { return d.etd; });

        bars.transition(1000)
          .attr("y", function(d) { return  y(d.count); } )
          .attr("height", function(d) { return height - y(d.count); } );

        bars.enter().append("rect")
          .attr("class", "bar")
          .attr("x", function(d) { return x(d.etd); })
          .attr("width", x(1 - 2 * binMargin))
          .attr("y", height)
          .attr("height", 0)
          .transition(1000)
            .attr("y", function(d) { return y(d.count); })
            .attr("height", function(d) { return height - y(d.count); });

        bars.exit()
          .transition(1000)
            .attr("y", height)
            .attr("height", 0)
          .remove();
      });
    }

    make_graph();

# HTML source

    :::html
    <!DOCTYPE html>
    <meta charset="utf-8">
    <head>
      <link rel="stylesheet" type="text/css" href="graph.css">
    </head>
    <body>
    <p>
      <label for="station_select"
              style="display: inline-block; width: 140px; text-align: right">
        Station =
      </label>
      <select id="station_select" onchange="update_url()">
        <option value="plza">El Cerrito Plaza</option>
        <option value="mont">Montgomery</option>
      </select>
      <label for="day_select"
              style="display: inline-block; width: 140px; text-align: right">
        Weekday =
      </label>
      <select id="day_select" onchange="update_url()">
        <option value="0">Weekday</option>
        <option value="1">Saturday</option>
        <option value="2">Sunday</option>
      </select>
      <label for="dest"
             style="display: inline-block; width: 140px; text-align: right">
             Destination =
      </label>
      <select id="dest" onchange="update_url()">
        <option value="Fremont">Fremont</option>
        <option value="Richmond">Richmond</option>
        <option value="Millbrae">Millbrae</option>
        <option value="Pittsburg/Bay Point">Pittsburg/Bay Point</option>
        <option value="Dublin/Pleasanton">Dublin/Pleasanton</option>
        <option value="SF Airport">SF Airport</option>
        <option value="SFO/Millbrae">SFO/Millbrae</option>
      </select>
    </p>
    <p>
      <label for="time"
             style="display: inline-block; align: left; width: 140px; text-align: right">
             Time = <span id="prettyTime">...</span>
           </label>
      <input type="range" id="time" min="240" max="1440" style="width:600px" value="460">
    </p>
    <p>
        Click slider and use arrow keys to adjust time.
    </p>
    <script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
    <script src="graph.js"></script>

# CSS source

    :::css
    body {
      width: 80%;
      margin-left: auto;
      margin-right: auto;
    }

    .bar {
      fill: steelblue;
    }

    .bar:hover {
      fill: brown;
    }

    .tick {
      width: 2px
    }

    .axis {
      font: 20px sans-serif;
      font-weight: bold;
    }

    .axis path,
    .axis line {
      fill: none;
      stroke: #000;
      stroke-width: 2;
      shape-rendering: crispEdges;
    }


# Conclusion

In this series of posts I've shown how to set up a Flask server on EC2, enable that server to respond to queries with data from a SQL database, populate that database with useful information and finally write a D3.js visualization using data provided by the Flask server.

##### _Four Part series on creating a D3.js graph powered by Flask and SQL_

1. [Running a Flask app on AWS EC2]({filename}/flask-on-ec2.md)
1. [Using Flask to answer SQL queries]({filename}/flask-sql.md)
1. [Getting csv data from requests to a SQL backed Flask app]({filename}/flask-bart-sql.md)
1. **A D3.js plot powered by a SQL database**
