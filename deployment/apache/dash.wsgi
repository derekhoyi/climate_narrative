import sys

# add your project directory to the sys.path
sys.path.insert(0, '/var/www/dash/')

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
from src.app import app
application = app.server