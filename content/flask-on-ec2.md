Title: Running a Flask app on AWS EC2
Date: 2-24-2015
Category: Tutorials
Tags: python, AWS

# 1. Starting up an EC2 instance

[Flask](http://flask.pocoo.org/) is a web framework for python, meaning that it provides a simple interface for dynamically generating responses to web requests. In this tutorial I set up a flask server on an Amazon Web Services EC2 instance. The server will respond to URLs with data from a SQL database. In a later post I'll show how to use this server to provide data for a D3.js plot where the user can request specific data to be plotted.

1. First we'll have to launch an EC2 instance. [Amazon has a tutorial here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance_linux.html), so I won't repeat it. There a few ways you'll want to differ from the tutorial:

    1. In step 3, select the Ubuntu Server 14.04 LTS (HVM) AMI (ami-29ebb519) instead of the Amazon Linux. The exact versions may change with time.
    1. In step 7b, configure the security groups as shown below. This setting allows access to port 80 (HTTP) from anywhere, and ssh access only from your IP address.

    <img src="/extra/images/aws_security_group.png" title="AWS security rules">

1. Follow Amazon's instructions to connect to your instance [here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-connect-to-instance-linux.html)

# 2. Setting up the instance

Now that we've connected to the instance, it's time to install some of the programs we'll need.

1. Install the apache webserver and mod_wsgi.

        :::console
        $ sudo apt-get update
        $ sudo apt-get install apache2
        $ sudo apt-get install libapache2-mod-wsgi

    At this point if you point your browser at your instance's public DNS name (see "connect to your instance" link above) you should see some version of the apache server's assuring "It works!" page.

    <img src="/extra/images/itworks.png" title="apache it works!">

2. We'll install Flask using the pip tool (which also needs to be installed).

        :::console
        $ sudo apt-get install python-pip
        $ sudo pip install flask

3. Create a directory for our flask app.
    We'll create a directory in our home directory to work in, and link to it from the site-root defined in apache's configuration (`/var/www/html` by defualt, see `/etc/apache2/sites-enabled/000-default.conf` for the current value).

        :::console
        $ mkdir ~/flaskapp
        $ sudo ln -sT ~/flaskapp /var/www/html/flaskapp

    To verify our linking operation is working, create an `index.html` file in our new directory.

        :::console
        $ cd ~/flaskapp
        $ echo "Hello World" > index.html

    You should now see "Hello World" displayed if you navigate to (`your instance public DNS`)/flaskapp in your browser.

    <img src="/extra/images/helloworldhtml.png" title="Hello World index.html">

# 3. Running a simple flask app
