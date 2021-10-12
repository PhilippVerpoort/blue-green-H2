from src.data import obtainScenarioData
from src.plotting import plotFig1

times = [2020, 2030, 2050]
fuelData, FSCPData = obtainScenarioData(times)

#print(fuelData.query("fuel == 'green RE' or fuel == 'green mix'"))
#print(fuelData.query("fuel == 'blue HEB' or fuel == 'blue LEB'"))

#print(fuelData)

exit()

showFuels = [(2020, 'natural gas'),
             (2020, 'blue HEB'),
             (2020, 'green RE'),
             (2050, 'green RE'),
]

showFSCPs = [(2020, 'natural gas', 2020, 'blue HEB'),
             (2020, 'natural gas', 2020, 'green RE'),
             (2020, 'natural gas', 2050, 'green RE'),
             (2020, 'blue HEB',    2020, 'green RE'),
             (2020, 'blue HEB',    2050, 'green RE'),
]

plotFig1(fuelData, FSCPData, showFuels=showFuels, showFSCPs=showFSCPs)