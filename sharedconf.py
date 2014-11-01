STATIC_PATHS = ['resources/favicon.png']
EXTRA_PATH_METADATA = {
    'resources/favicon.png' : {
        'path' : 'favicon.ico'
    },
}

AUTHOR = u'Frank Cleary'
SITENAME = u'Data Science Bytes'

PATH = 'content'

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

# Social widget
SOCIAL = (('Twitter', 'https://twitter.com/DSBytes'),)

DEFAULT_PAGINATION = 20

# Twitter button
TWITTER_USERNAME = 'DSBytes'
