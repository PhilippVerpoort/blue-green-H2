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
[1] George, J. F., Müller, V. P., Winkler, J. & Ragwitz, M. Is blue hydrogen a bridging technology? - The limits of a CO2 price and the role of state-induced price components for green hydrogen production in Germany. Energy Policy 167, 113072 (2022).

[2] Bauer, C. et al. On the climate impacts of blue hydrogen production. Sustainable Energy & Fuels 00, 1–10 (2021).

[3] IEA. Global Methane Tracker 2022. https://www.iea.org/reports/global-methane-tracker-2022 (2022).

[4] IEAGHG. Techno-Economic Evaluation of SMR Based Standalone (Merchant) Hydrogen Plant with CCS (2017).

[5] Smith, E. et al. The cost of CO2 transport and storage in global integrated assessment modeling. International Journal of Greenhouse Gas Control 109, 103367 (2021).

[6] Budinis, S., Krevor, S., Dowell, N. M., Brandon, N. & Hawkes, A. An assessment of CCS costs, barriers and potential. Energy Strategy Reviews 22, 61–81 (2018).

[7] AEMO. 2022 Integrated System Plan (2022).

[8] IEA. Global Hydrogen Review 2022. https://www.iea.org/reports/global-hydrogen-review-2022 (2022).

[9] IEA. The Future of Hydrogen: Seizing today’s opportunities. (OECD, 2019). doi:10.1787/1e0514c4-en.

[10] Staiß, F. et al. Optionen für den Import grünen Wasserstoffs nach Deutschland bis zum Jahr 2030. 128.

[11] Zeyen, Elisabeth, Riepin, Iegor & Brown, Tom. Hourly versus annually matched renewable supply for electrolytic hydrogen. https://zenodo.org/record/7457441 (2022) doi:10.5281/ZENODO.7457441.

[12] Rödl, A., Wulf, C. & Kaltschmitt, M. Assessment of Selected Hydrogen Supply Chains—Factors Determining the Overall GHG Emissions. in Hydrogen Supply Chains 81–109 (Elsevier, 2018). doi:10.1016/B978-0-12-811197-0.00003-8.

[13] United States Department of Energy. The Inflation Reduction Act Drives Significant Emissions Reductions and Positions America to Reach Our Climate Goals. (2022).

[14] IEA. World Energy Outlook (2023).

[15] IRENA. Green hydrogen cost reduction: Scaling up electrolysers to meet the 1.5C climate goal. 106 (2020).

[16] IEA (2023), Net Zero Roadmap: A Global Pathway to Keep the 1.5 °C Goal in Reach, IEA, Paris https://www.iea.org/reports/net-zero-roadmap-a-global-pathway-to-keep-the-15-0c-goal-in-reach, License: CC BY 4.0

[17] IEA (2023), Global Hydrogen Review 2023, IEA, Paris https://www.iea.org/reports/global-hydrogen-review-2023, License: CC BY 4.0
