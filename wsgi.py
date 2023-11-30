import sys, os
sys.path.insert(0,os.path.dirname(__file__))

from webapp import webapp

webapp.start()
application = webapp.flask_app
