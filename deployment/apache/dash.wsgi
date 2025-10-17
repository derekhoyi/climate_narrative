import sys

# add your project directory to the sys.path
sys.path.insert(0, '/storage/climate_narrative/src')

activate_this = '/storage/climate_narrative/venv/bin/activate_this.py'
with open(activate_this) as file_:
   exec(file_.read(), dict(__file__=activate_this))

# need to pass the flask app as "application" for WSGI to work
# for a dash app, that is at app.server
from app import app
application = app.server