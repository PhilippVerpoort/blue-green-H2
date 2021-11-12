#!/usr/bin/env python
# run this script and navigate to http://127.0.0.1:8050/ in your web browser


from src.app.app import app
from src.data.scenario_input_default import scenarioInputDefault
from src.app.layout import setLayout


# define layout
setLayout(app, scenarioInputDefault)


# import and list callbacks (list so they don't get removed as unused imports)
from src.app.callbacks import callbackUpdate, callbackDownloadConfig, callbackWidget1, callbackWidget2, callbackDownloadExportdata
callbackUpdate, callbackDownloadConfig, callbackWidget1, callbackWidget2, callbackDownloadExportdata


# for running as Python script in standalone
if __name__ == '__main__':
    app.run_server(debug=True)
