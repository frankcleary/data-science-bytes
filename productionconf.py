#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Frank Cleary'
SITENAME = u'Data Science Bytes'
SITEURL = 'http://www.datasciencebytes.com'
THEME = 'themes/notmyidea'

PATH = 'content'
STATIC_PATHS = ['extra/favicon2.png',
                'extra/images',
                'extra/ipynb',
                'extra/timeseries.txt']
EXTRA_PATH_METADATA = {
    'extra/favicon2.png': {'path': 'favicon.ico'},
}

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = u'en'

# URL/Save as schemes
ARTICLE_URL = 'bytes/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'bytes/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
YEAR_ARCHIVE_URL = 'bytes/{date:%Y}/'
YEAR_ARCHIVE_SAVE_AS = 'bytes/{date:%Y}/index.html'
MONTH_ARCHIVE_URL = 'bytes/{date:%Y}/{date:%m}/'
MONTH_ARCHIVE_SAVE_AS = 'bytes/{date:%Y}/{date:%m}/index.html'


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

# Twitter button
TWITTER_USERNAME = 'DSBytes'

DISQUS_SITENAME = 'datasciencebytes' 

# Google Analytics
GOOGLE_ANALYTICS = 'UA-47982219-2'
