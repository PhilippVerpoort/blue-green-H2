#!/bin/bash

types=(smr heb leb);
capex=(222.89 263.91 398.48);

for i in 0 1 2; do
    head -n1 regression_data_blue_all.csv > regression_data_blue_${types[$i]}.csv
    awk -F, "\$4==${capex[$i]} {print \$0;}" regression_data_blue_all.csv >> regression_data_blue_${types[$i]}.csv
done
