# Cost competitiveness of blue and green H2
This repository provides data and codes used in the analysis of the cost competitiveness of blue and green hydrogen supply options.


## Getting started
If you would like to try to run this software, then you may want to install all associated Python packages with [poetry](https://python-poetry.org/) first, and switch to the shell of the associated venv. Once complete, you can simply run the scripts by calling `plot.py`.

```
poetry install
poetry shell
```

Alternatively, you can install the required packages using `pip`, perhaps after creating a venv by some other means:

```
pip install plotly pandas openpyxl PyYAML kaleido
```

If you also want to be able to run the webapp, then you will also need these packages:

```
pip install dash dash-bootstrap-components
```


## Running the webapp
The webapp can be started by running

```
python webapp.py
```

and then navigating to the provided IP address and port provided in your terminal, which is usually `http://127.0.0.1:8050/`.

The file `wsgi.py` can be used to make the webapp accessible from a WSGI-enable webserver (such as Apache2). There is a lot of information available on this matter, a suitable point to start would for instance be [here](https://flask.palletsprojects.com/en/2.0.x/deploying/mod_wsgi/).


## License
The codes and other content provided in this repository are available under the [MIT License](https://opensource.org/licenses/MIT), a copy of which is also provided as a separate file in this repository.
