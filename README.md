# Research software used for the techno-economic analysis of the cost competitiveness of blue and green hydrogen

## Summary
This repository make source codes and input data publicly available that were used in the analysis of the cost competitiveness of blue and green hydrogen  supply options in an accompanying article and interactive webapp.

## How to cite this work

**This software (source code and input data):**
Verpoort, Philipp C.; Ueckerdt, Falko; Anantharaman, Rahul; Bauer, Christian; Beck, Fiona; Longden, Thomas; Roussanaly, Simon (2023): Research software used for the techno-economic analysis of the cost competitiveness of blue and green hydrogen. V. 3.0.3. GFZ Data Services. https://doi.org/10.5880/pik.2023.007

**The accompanying interactive webapp:**
Verpoort, Philipp C.; Ueckerdt, Falko; Anantharaman, Rahul; Bauer, Christian; Beck, Fiona; Longden, Thomas; Roussanaly, Simon (2023): Interactive webapp for techno-economic analysis of the cost competitiveness of blue and green hydrogen. V. 3.0.3. GFZ Data Services. https://doi.org/10.5880/pik.2023.006

**The accompanying peer-reviewed article:**
Ueckerdt et al., On the cost competitiveness of blue and green hydrogen, Joule (2024). https://doi.org/10.1016/j.joule.2023.12.004

## How to use this software

#### Run hosted service online:
This source code can be installed and executed to reproduce all the results (mainly figures) presented in the accompanying article and to run the interactive webapp. Note that the webapp is also hosted as a public service here: https://doi.org/10.5880/pik.2023.006

#### Install dependencies:
If you would like to try to execute this software locally on your machine, then you will need to have its Python dependencies installed.

The easiest way to accomplish this is via [poetry](https://python-poetry.org/):
```commandline
poetry install
```

Alternatively, you can install the required packages using `pip` (potentially following the creation of a virtual environment):

```commandline
pip install git+https://github.com/PhilippVerpoort/piw.git@v0.8.1
pip install pandas openpyxl kaleido pyyaml
```

#### Export figures manually
After activating the virtual environment (e.g. via `poetry shell`), please use:
```commandline
python export.py
```
This will export all figures. Alternatively, you may choose to export only Fig. 1 by using:
```commandline
python export.py fig1
```

#### Running the interactive webapp
The interactive webapp, which is also hosted [here](https://doi.org/10.5880/pik.2023.006), can be run via: 
```commandline
python webapp.py
```
and then navigating to the provided IP address and port provided in your terminal, which is usually http://127.0.0.1:8050/.


## Licence
The source code in this repository is available under an [MIT Licence](https://opensource.org/licenses/MIT), a copy of which is also provided as a separate file in this repository.


## References
The following references are cited in input-data files in the `data/` subdirectory.

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
