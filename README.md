# pairwise_fst
Calculating Pairwise Fst with Plink and Python

Written by Lane M Atmore Dec 2020

pairwise_fst.py will run FST calculations on all pairwise populations within a fam file for any given dataset. 
No additional files are necessary other than the plink data.

pairwise_fst.py calls plink through bash, which means you need to have
plink installed in your bin (on mac /usr/local/bin) for the program to run 
properly. https://zzz.bwh.harvard.edu/plink/download.shtml

Python modules required: pandas-plink, numpy, pandas

Syntax to use pairwise_fst.py in a unix terminal is: \
python pairwise_fst.py < your file prefix >

It is recommended to place pairwise_fst.py in the same directory as your data.

pairwise_fst.py uses the Rscript matrix.R
matrix.R should be in the same directory as pairwise_fst.py

It takes a minute or two to finish running.
A new folder named "Output" will be created
Within this folder is your paired populations (CSV), a pairwise FST matrix (CSV), and
a distance matrix of your data built in R (PDF). Also within Output/ will be the folder
"PLINK_out". This folder will contain .clust files that were input to PLINK and 
.fst, .nosex, and .log files for each pairwise FST calculation.

If you have a really big dataset DO NOT run on a local HD with limited space!!!
