#!/usr/bin/env python
# run this script and navigate to http://127.0.0.1:8050/ in your web browser


from src.app.app import app
from src.config_load import input_data
from src.app.layout.layout import initLayout


# define layout
initLayout(app, input_data)


# import and list callbacks (list so they don't get removed as unused imports)
from src.app.callbacks.callbacks import callbackUpdate, callbackDownloadConfig, callbackTableColour, callbackDownloadExportdata
callbackUpdate, callbackDownloadConfig, callbackTableColour, callbackDownloadExportdata


# define server for wsgi
server = app.server


# for running as Python script in standalone
if __name__ == '__main__':
    app.run_server(debug=True)
