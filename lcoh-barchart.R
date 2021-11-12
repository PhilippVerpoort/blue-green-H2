library(dplyr)
library(ggplot2)

###### Blue Data Regression Analysis ######

# economics stuff
i <- 0.08
n <- 25
epsilon <- i*(1+i)^n/((1+i)^n-1)

# physics stuff
ci_ng <- 198/10^6 # CI of NG: 55 kgCO2eq/GJ = 198 gCO2eq/kWh = 198e-6 tCO2eq/kWh
ohrs <- 8322.0

plotData = data.frame()

# regression analysis
order = c(smr=1,heb=2,leb=3)
for(type in c('smr', 'heb', 'leb')) {
    blueData <- read.csv(paste0('./input/regression/regression_data_blue_', type, '.csv'))

    blueData <- blueData %>% mutate(LCOH   = .[[1]]/3.0,                    # EUR/Nm³_H2 to EUR/kWh_LHV
                                    p_ng   = .[[2]] * 3.6/1000.0,           # EUR/GJ to EUR/kWh
                                    c_CTS  = .[[3]],                        # EUR/tCO2
                                    C_pl   = .[[4]] * 10^6,                 # MEUR to EUR
                                    emi    = .[[5]] * 1.0/3000.0,           # kgCO2/Nm³_H2 to tCO2eq/kWh_H2-LHV
                                    fOnM_pl= .[[8]] * 10^6,                 # MEUR to EUR
                                    vOnM_pl= .[[9]] * 10^6,                 # MEUR to EUR
                                    P_pl   = 1 * 3*10^5                     # Nm3/h to kW
                                   ) %>% select(LCOH, p_ng, c_CTS, C_pl, emi, fOnM_pl, vOnM_pl, P_pl, eff, CR)
                                   
    thisData <- blueData %>% slice(2:2) %>% mutate(type = paste0(order[type],"-",type))
                                   
    plotData <- rbind(plotData, thisData %>% mutate(variable = "IEAGHG", type = paste0(type,"-full")))
                                   
    plotData <- rbind(plotData, thisData %>% mutate(variable = "CapCost", LCOH = epsilon*C_pl/(P_pl*ohrs)))
    plotData <- rbind(plotData, thisData %>% mutate(variable = "fixedOnMCost", LCOH = fOnM_pl/(P_pl*ohrs)))
    plotData <- rbind(plotData, thisData %>% mutate(variable = "varOnMCost", LCOH = vOnM_pl/(P_pl*ohrs)))
    plotData <- rbind(plotData, thisData %>% mutate(variable = "FuelCost", LCOH = p_ng/eff))
    plotData <- rbind(plotData, thisData %>% mutate(variable = "CTSCost", LCOH = c_CTS*emi))
}

print(plotData %>% select(type, variable, LCOH))

fig <- ggplot() +
       geom_bar(aes(x=type, y=LCOH), data=plotData %>% filter(variable=="IEAGHG"), position="stack", stat="identity") +
       geom_bar(aes(x=type, y=LCOH, fill=variable), data=plotData %>% filter(variable!="IEAGHG"), position="stack", stat="identity")

ggsave(filename="output/lcoh-barchart.png")
