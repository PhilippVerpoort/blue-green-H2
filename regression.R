library(dplyr)

###### Green Data Regression Analysis ######

# economics stuff
i <- 0.08
n <- 25
epsilon <- i*(1+i)^n/((1+i)^n-1)

USD_to_EUR <- 0.86

# physics stuff
eff <- 0.7 # electrolysis efficiency of ~70%

# regression analysis
greenData <- read.csv("./input/regression/regression_data_green.csv")

greenData <- greenData %>% mutate(LCOH  = .[[1]] * USD_to_EUR/33.33,        # USD/kg to EUR/kWh
                                  p_el  = .[[2]] * USD_to_EUR/1000.0,       # USD/MWh to EUR/kWh
                                  c_L   = .[[3]] * USD_to_EUR,              # USD/kW to EUR/kW
                                  OCF   = .[[4]] * 1.0/100.0                # 100% to 1.0
                                 ) %>% select(LCOH, p_el, c_L, OCF)

model <- nls(LCOH ~ alpha * epsilon*c_L/(8760*(OCF*(1+(theta-1)*log(OCF)))) + gamma * p_el/eff, data=greenData, start=list(alpha=1.0, gamma=1.0, theta=1.0))
print(summary(model))
print(modelr::rsquare(model, greenData))



###### Blue Data Regression Analysis ######

# economics stuff
i <- 0.08
n <- 25
epsilon <- i*(1+i)^n/((1+i)^n-1)

# physics stuff
ci_ng <- 198/10^6 # CI of NG: 55 kgCO2eq/GJ = 198 gCO2eq/kWh = 198e-6 tCO2eq/kWh

# regression analysis
for(type in c('smr', 'heb', 'leb')) {
    blueData <- read.csv(paste0('./input/regression/regression_data_blue_', type, '.csv'))

    blueData <- blueData %>% mutate(LCOH  = .[[1]],                 # EUR/kWh
                                    p_ng  = .[[2]] * 3.6/1000.0,    # EUR/GJ to EUR/kWh
                                    c_CTS = .[[3]],                 # EUR/tCO2
                                    C_pl  = .[[4]] * 10^6,          # MEUR to EUR
                                    emi   = .[[5]] * 1.0/3000.0,    # kgCO2/Nm³_H2 to tCO2eq/kWh_H2-LHV
                                    P_pl  = 1 * 3*10^5              # Nm3/h to kW
                                   ) %>% select(LCOH, p_ng, c_CTS, C_pl, emi, P_pl, eff, CR)

    if(type == 'smr') {
        model <- nls(LCOH ~ alpha * epsilon*C_pl/(P_pl*8760) + gamma * p_ng/eff, data=blueData, start=list(alpha=1.0, gamma=1.0))
        print(summary(model))
        print(modelr::rsquare(model, blueData))
    }
    else {
        # using official capture rate from report
        model <- nls(LCOH ~ alpha * epsilon*C_pl/(P_pl*8760) + gamma * p_ng/eff + mu * c_CTS*emi, data=blueData, start=list(alpha=1.0, gamma=1.0, mu=1.0))
        print(summary(model))
        print(modelr::rsquare(model, blueData))
        
        # using own computed capture rate
        model <- nls(LCOH ~ alpha * epsilon*C_pl/(P_pl*8760) + gamma * p_ng/eff + mu * CR*ci_ng*c_CTS/eff, data=blueData, start=list(alpha=1.0, gamma=1.0, mu=1.0))
        print(summary(model))
        print(modelr::rsquare(model, blueData))
    }
}
