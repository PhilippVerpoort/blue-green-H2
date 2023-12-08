#!/bin/bash

mkdir -p ./production/

# requires pdfjam (via texlive-extra-utils)
# documentation: https://github.com/rrthomas/pdfjam / https://ctan.mirror.garr.it/mirrors/ctan/macros/latex/contrib/pdfpages/pdfpages.pdf

# Fig. 1
pdfjam --papersize '{86mm,61mm}' ./print/fig1A.pdf -o ./production/fig1A.pdf
pdfjam --papersize '{86mm,61mm}' ./print/fig1B.pdf -o ./production/fig1B.pdf
pdfjam ./print/fig1{A,B}.pdf --nup 2x1 --papersize '{172mm,61mm}' --outfile ./production/fig1.pdf
rm ./production/fig1{A,B}.pdf

# Fig. 3
pdfjam --papersize '{172mm,122mm}' ./print/fig3.pdf -o ./production/fig3.pdf

# Fig. 4
pdfjam --papersize '{86mm,100mm}' ./print/fig4A.pdf -o ./production/fig4A.pdf
pdfjam --papersize '{86mm,100mm}' ./print/fig4B.pdf -o ./production/fig4B.pdf
pdfjam ./print/fig4{A,B}.pdf --nup 2x1 --papersize '{172mm,100mm}' --outfile ./production/fig4.pdf
rm ./production/fig4{A,B}.pdf

# Fig. 5
pdfjam --papersize '{172mm,100mm}' ./print/fig5.pdf -o ./production/fig5.pdf
