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


## References
AEMO (2022) 2022 Integrated System Plan (SC). URL: https://aemo.com.au/energy-systems/major-publications/integrated-system-plan-isp/2022-integrated-system-plan-isp

Bauer, Christian; Treyer, Karin; Antonini, Cristina; Bergerson, Joule; Gazzani, Matteo; Gencer, Emre; et al. (2021): On the climate impacts of blue hydrogen production. Sustainable Energy & Fuels. https://doi.org/10.1039/D1SE01508G

Budinis, Sara; Krevor, Samuel; Dowell, Niall Mac; Brandon, Nigel; Hawkes, Adam (2018): An assessment of CCS costs, barriers and potential. Energy Strategy Reviews. https://doi.org/10.1016/j.esr.2018.08.003

George, Jan Frederick; Müller, Viktor Paul; Winkler, Jenny; Ragwitz, Mario (2022): Is blue hydrogen a bridging technology? - The limits of a CO2 price and the role of state-induced price components for green hydrogen production in Germany. Energy Policy. https://doi.org/10.1016/j.enpol.2022.113072

IEA (2019). The Future of Hydrogen. OECD. https://doi.org/10.1787/1e0514c4-en

IEA (2022a). Global Hydrogen Review 2022. URL: https://www.iea.org/reports/global-hydrogen-review-2022

IEA (2022b). Global Methane Tracker 2022. URL: https://www.iea.org/reports/global-methane-tracker-2022

IEA (2023a). Global Hydrogen Review 2023. URL: https://www.iea.org/reports/global-hydrogen-review-2023

IEA (2023b). Net Zero Roadmap: A Global Pathway to Keep the 1.5 °C Goal in Reach. URL: https://www.iea.org/reports/net-zero-roadmap-a-global-pathway-to-keep-the-15-0c-goal-in-reach

IEA (2023c). World Energy Outlook 2023. URL: https://www.iea.org/reports/world-energy-outlook-2023

IEAGHG (2017). Techno-Economic Evaluation of SMR Based Standalone (Merchant) Hydrogen Plant with CCS (2017). URL: https://ieaghg.org/publications/technical-reports/reports-list/9-technical-reports/784-2017-02-smr-based-h2-plant-with-ccs

IRENA (2020). Green hydrogen cost reduction: Scaling up electrolysers to meet the 1.5C climate goal. 106. URL: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2020/Dec/IRENA_Green_hydrogen_cost_2020.pdf

Rödl, Anne; Wulf, Christina; Kaltschmitt, Martin (2018): Hydrogen Supply Chains. . https://doi.org/10.1016/B978-0-12-811197-0.00003-8

Smith, Erin; Morris, Jennifer; Kheshgi, Haroon; Teletzke, Gary; Herzog, Howard; Paltsev, Sergey (2021): The cost of CO2 transport and storage in global integrated assessment modeling. International Journal of Greenhouse Gas Control. https://doi.org/10.1016/j.ijggc.2021.103367

Staiß, F. et al. Optionen für den Import grünen Wasserstoffs nach Deutschland bis zum Jahr 2030. 128. URL: https://www.acatech.de/publikation/wasserstoff/

United States Department of Energy (2022). The Inflation Reduction Act Drives Significant Emissions Reductions and Positions America to Reach Our Climate Goals. URL: https://www.energy.gov/sites/default/files/2022-08/8.18%20InflationReductionAct_Factsheet_Final.pdf

Zeyen, E., Riepin, I., & Brown, T. (2022). Hourly versus annually matched renewable supply for electrolytic hydrogen (Version 0.1). Zenodo. https://doi.org/10.5281/zenodo.7457441
