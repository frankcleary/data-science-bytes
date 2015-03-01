Title: Running a Flask app on AWS EC2
Date: 2-24-2015
Category: Tutorials
Tags: python, AWS

# 1. Starting up an EC2 instance

[Flask](http://flask.pocoo.org/) is a web framework for python, meaning that it provides a simple interface for dynamically generating responses to web requests. In this tutorial I set up a flask server on an Amazon Web Services EC2 instance. In [another post]({filename}/flask-sql.md) we'll set up the server to respond to requests with data from a SQL database. In a later post I'll show how to use this server to provide data for a D3.js plot where the user can request specific data to be plotted.

#### 1. Launch an EC2 instance.

[Amazon has a tutorial here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance_linux.html), so I won't repeat it. There a few ways you'll want to differ from the tutorial:

1. In step 3, select the Ubuntu Server 14.04 LTS (HVM) AMI (ami-29ebb519) instead of the Amazon Linux. The exact versions may change with time.
2. In step 7b, configure the security groups as shown below. This setting allows access to port 80 (HTTP) from anywhere, and ssh access only from your IP address.

<img src="/extra/images/flaskec2/aws_security_group.png" title="AWS security rules">

#### 2. Follow Amazon's instructions to connect to your instance [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-connect-to-instance-linux.html)

# 2. Setting up the instance

Now that we've connected to the instance, it's time to install some of the programs we'll need.

#### 1. Install the apache webserver and mod_wsgi.

    :::console
    $ sudo apt-get update
    $ sudo apt-get install apache2
    $ sudo apt-get install libapache2-mod-wsgi

If you point your browser at your instance's public DNS name (see "connect to your instance" link above) you should see some version of the apache server's assuring "It works!" page.

<img src="/extra/images/flaskec2/itworks.png" title="apache it works!">

#### 2. Install Flask using the pip tool (which also needs to be installed).

    :::console
    $ sudo apt-get install python-pip
    $ sudo pip install flask

#### 3. Create a directory for our flask app.

We'll create a directory in our home directory to work in, and link to it from the site-root defined in apache's configuration (`/var/www/html` by defualt, see `/etc/apache2/sites-enabled/000-default.conf` for the current value).

    :::console
    $ mkdir ~/flaskapp
    $ sudo ln -sT ~/flaskapp /var/www/html/flaskapp

To verify our operation is working, create a simple `index.html` file.

    :::console
    $ cd ~/flaskapp
    $ echo "Hello World" > index.html

You should now see "Hello World" displayed if you navigate to `(your instance public DNS)/flaskapp` in your browser.

<img src="/extra/images/flaskec2/helloworldhtml.png" title="Hello World index.html">

# 3. Running a simple flask app

#### 1. Create an app.

We'll use the simple "Hello world" [example](http://flask.pocoo.org/docs/0.10/quickstart/) from the flask documentation. Put the following content in a file named `flaskapp.py`:

    :::python
    from flask import Flask
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
      return 'Hello from Flask!'

    if __name__ == '__main__':
      app.run()

#### 2. Create a .wsgi file to load the app.

Put the following content in a file named `flaskapp.wsgi`:

    :::python
    import sys
    sys.path.insert(0, '/var/www/html/flaskapp')

    from flaskapp import app as application


#### 3. Enable mod_wsgi.

The apache server displays html pages by default but to serve dynamic content from a Flask app we'll have to make a few changes. In the apache configuration file located at `/etc/apache2/sites-enabled/000-default.conf`, add the following block just after the `DocumentRoot /var/www/html` line:

    WSGIDaemonProcess flaskapp threads=5
    WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi

    <Directory flaskapp>
        WSGIProcessGroup flaskapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>

<img src="/extra/images/flaskec2/apacheconf.png" title="Apache wsgi config">

#### 4. Restart the webserver.

Use this command to restart the server with the new configuration

    :::console
    $ sudo apachectl restart

#### 5. Test configuration.

If you navigate your browser to your EC2 instance's public DNS again, you should see the text returned by the hello_world function of our app, "Hello from Flask!"

<img src="/extra/images/flaskec2/hellofromflask.png" title="Hello from flask">

Our server is now running and ready to crunch some data (if something isn't working, try checking the log file in `/var/log/apache2/error.log`).

# 4. Have Flask app do work

Now that we have a server ready to do work we'll set up a simple service to provide letter counts from an input string.

#### 1. Collect information from the url.

Flask allows us to route requests to functions based on the url requested. We can also get input from the url to pass into the function. Add the following to flaskapp.py:

    :::python
    @app.route('/countme/<input_str>')
    def count_me(input_str):
        return input_str

This `count_me()` function will return anything after the `countme/` portion of the url. Restart the webserver to see it in action:

    :::console
    $ sudo apachectl restart

<img src="/extra/images/flaskec2/countmebasic.png" title="Basic flask function">

#### 2. Process information

Let's make our `count_me()` function a little more interesting. Modify flaskapp.py like so:

    :::python
    from collections import Counter

    ...

    @app.route('/countme/<input_str>')
    def count_me(input_str):
        input_counter = Counter(input_str)
        response = []
        for letter, count in input_counter.most_common():
            response.append('"{}"": {}'.format(letter, count))
        return '<br>'.join(response)


Restart the server and view the results:

    :::console
    $ sudo apachectl restart

<img src="/extra/images/flaskec2/countme.png" title="Flask word counter">

* Note that it is bad practice to format html responses inside these functions, [templates](http://flask.pocoo.org/docs/0.10/templating/) should generally be used instead.
* The entire `count_me()` function could be written in one logical line:

        :::python
        return '<br>'.join('"{}": {}'.format(let, cnt)
                           for let, cnt in Counter(in_str).most_common())

# Using Flask to query a SQL database

See [this post]({filename}/flask-sql.md) for a description of how to connect flask to a SQL database.
