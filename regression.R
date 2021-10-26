library(dplyr)



###### Green Data Regression Analysis  ######

# economics stuff
i <- 0.08
n <- 25
epsilon <- i*(1+i)^n/((1+i)^n-1)

USD_to_EUR <- 0.86

# physics stuff
ci_ng <- 0.198 # CI of NG: tCO2eq/kWh
eff <- 0.7

greenData <- read.csv("./input/regression/regression_data_green.csv")

greenData <- greenData %>% mutate(LCOH  = .[[1]] * USD_to_EUR/33.33,        # USD/kg to EUR/kWh
                                  p_el  = .[[2]] * USD_to_EUR/1000.0,       # USD/MWh to EUR/kWh
                                  c_L   = .[[3]] * USD_to_EUR,              # USD/kW to EUR/kW
                                  OCF   = .[[4]] * 1.0/100.0                # 100% to 1.0
                                 ) %>% select(LCOH, p_el, c_L, OCF)

model <- nls(LCOH ~ alpha * epsilon*c_L/(8760*(OCF*(1+(theta-1)*log(OCF)))) + gamma * p_el/eff, data=greenData, start=list(alpha=1.0, gamma=1.0, theta=1.0))
coefs <- coef(model)
print(summary(model))
print(modelr::rsquare(model, greenData))



###### Blue Data Regression Analysis  ######

# economics stuff
i <- 0.08
n <- 25
epsilon <- i*(1+i)^n/((1+i)^n-1)

# physics stuff
ci_ng <- 198/10^6 # CI of NG: 55 kgCO2eq/GJ = 198 gCO2eq/kWh = 198e-6 tCO2eq/kWh

# variables of different production types
eff <- c(smr = 0.7, heb = 0.6, leb = 0.5)
cr <- c(smr = 0.0, heb = 0.60, leb = 0.90)

for(type in c('smr', 'heb', 'leb')) {
    blueData <- read.csv(paste0('./input/regression/regression_data_blue_', type, '.csv'))

    blueData <- blueData %>% mutate(LCOH  = .[[1]],                 # EUR/kWh
                                    p_ng  = .[[2]] * 3.6/1000.0,    # EUR/GJ to EUR/kWh
                                    c_CTS = .[[3]],                 # EUR/tCO2
                                    C_pl  = .[[4]] * 10^6,          # MEUR to EUR
                                    P_pl  = 1 * 3*10^5              # Nm3/h to kW
                                   ) %>% select(LCOH, p_ng, c_CTS, C_pl, P_pl)

    if(type == 'smr') {
        model <- nls(LCOH ~ alpha * epsilon*C_pl/(P_pl*8760) + gamma * p_ng/eff[type], data=blueData, start=list(alpha=1.0, gamma=1.0))
    }
    else {
        model <- nls(LCOH ~ alpha * epsilon*C_pl/(P_pl*8760) + gamma * p_ng/eff[type] + mu * cr[type]*ci_ng*c_CTS/eff[type], data=blueData, start=list(alpha=1.0, gamma=1.0, mu=1.0))
    }
    coefs <- coef(model)
    print(summary(model))
    print(modelr::rsquare(model, blueData))
}
