Title: Running a Flask app on AWS EC2
Date: 2-24-2015
Category: Tutorials
Tags: python, AWS

# 1. Setting up an EC2 instance

[Flask](http://flask.pocoo.org/) is a web framework for python, meaning that it provides a simple interface for dynamically generating responses to web requests. In this tutorial I set up a flask server on an Amazon Web Services EC2 instance. The server will respond to URLs with data from a SQL database. In a later post I'll show how to use this server to provide data for a D3.js plot where the user can request specific data to be plotted.

1. First we'll have to launch an EC2 instance. [Amazon has a tutorial here](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance_linux.html), so I won't repeat it. There a few ways you'll want to differ from the tutorial:

    1. In step 3, select the Ubuntu Server 14.04 LTS (HVM) AMI (ami-29ebb519) instead of the Amazon Linux. The exact versions may change with time.
    1. In step 7b, configure the security groups as shown below. This setting allows access to port 80 (HTTP) from anywhere, and ssh access only from your IP address.

    <img src="/extra/images/aws_security_group.png" title="AWS security rules">
