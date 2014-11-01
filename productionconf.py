#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from sharedconf import *

SITEURL = 'http://www.datasciencebytes.com'
THEME = 'themes/notmyidea-cms'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('Recommended Books', SITEURL + '/recommended-books'),
         ('Recommended Videos', SITEURL + '/recommended-videos'),)

# Social widget
SOCIAL = (('Twitter', 'https://twitter.com/DSBytes'),)

DEFAULT_PAGINATION = 20

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = False

DISQUS_SITENAME = 'datasciencebytes' 

# Google Analytics
GOOGLE_ANALYTICS = 'UA-47982219-2'
