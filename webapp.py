#!/usr/bin/env python
# run this script and navigate to http://127.0.0.1:8050/ in your web browser


from src.app.app import dash_app as dash_app
from src.app.layout.layout import getLayout


# define layout
dash_app.layout = getLayout(dash_app.get_asset_url("logo.png"))


# import and list callbacks (list so they don't get removed as unused imports)
from src.app.callbacks.callbacks import callbackUpdate, callbackDownloadConfig, callbackTableColour, callbackDownloadExportdata
callbackUpdate, callbackDownloadConfig, callbackTableColour, callbackDownloadExportdata


# define flask_app for wsgi
flask_app = dash_app.server


# for running as Python script in standalone
if __name__ == '__main__':
    dash_app.run_server(debug=False)
