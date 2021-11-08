#!/usr/bin/env python
# run this script and navigate to http://127.0.0.1:8050/ in your web browser

from server import app
from src.app.callbacks import callback1

# list all callbacks once so they don't get removed as unused imports
callback1

# for running as Python script in standalone
if __name__ == '__main__':
    app.run_server(debug=True)
