#!/usr/bin/env python

#script for wrapping Fst function from PLINK
#This should output a pairwise Fst matrix 
#All you need as input is your plink bfiles

import numpy as np
import subprocess
import sys
import os
from os import path
import io
import pandas as pd
import csv
from pandas_plink import read_plink
import re

#arg1 is the prefix for the PLINK bfiles

prefix = str(sys.argv[1])

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#Check args
def check_args(prefix):
	if (len(sys.argv) > 2):
		print("Too many arguments specified")
		exit()
	elif (len(sys.argv) <= 0):
		print("Too few arguments specified - did you forget to give your bfile prefix?")
		exit()
	else:
		pass
check_args(prefix)

print("Running with file prefix " + prefix)

def check_output():
	if path.exists('output'):
		print('Please remove the output folder from your previous run before running again')
		exit()
	else:
		pass
check_output()

#First thing we need to do is create the pairwise table for calculating Fst between
#all populations

def pairwise_fst(prefix):
	#get unique fids
	(bim, fam, bed) = read_plink(prefix, verbose = True)
	print("Bfiles mapped")
	
	unique_fam = pd.DataFrame(fam['fid'].unique())
	
	fam_list = unique_fam[0].tolist()
	fam_list2 = unique_fam[0].tolist()

	#create pairwise df
	index = pd.MultiIndex.from_product([fam_list, fam_list2], names = ['pop1', 'pop2'])
	paired_df = pd.DataFrame(index = index).reset_index()
	
	paired_df['pops'] = paired_df[['pop1','pop2']].agg('.'.join, axis = 1)
	
	os.mkdir('output')
	os.chdir('output')
	
	paired_df['pops'].to_csv('paired_pops.csv', index = False, header = False)

	print("Populations paired")

	#Now we need to calculate pairwise FST for all pairs in the pairwise csv file
	#What needs to be done: create clust files for each population pair
	#This means for each pair we need to grab all the info from the fam file and print to a clust
	#Then we use the clust to calculate fst for the pair of populations

	paired_list1 = paired_df['pop1'].to_list()
	paired_list2 = paired_df['pop2'].to_list()

	original_stdout = sys.stdout
	
	filtered_fam = pd.DataFrame(fam[['fid','iid']])
	filtered_fam['group'] = filtered_fam['fid']
	
	for (a,b) in zip(paired_list1, paired_list2):
		filtered_fam.loc[filtered_fam['fid'].isin([a,b])].to_csv(str(a) + '.' + str(b) + '.clust', 
		encoding = 'utf-8', sep = '\t', index = False, header = False)
	
	os.chdir('../')
	
	#calculate FST with plink
	FST = subprocess.Popen('for i in $(less output/paired_pops.csv); do \
	plink --bfile' + ' ' + prefix + ' ' + '--within output/$i.clust --double-id --fst \
	--allow-no-sex --out output/$i; done', shell = True)
	
	FST.communicate()
	print("Fst Calculated")

	#Now we need the pop names and mean fst values from the log files		
	#create lists for pops and FST
	
	os.chdir('output')
	#grab the values we need from all the files
	pops = []
	fst = []
	pattern1 = re.compile('Mean Fst', re.IGNORECASE)
	pattern2 = re.compile('Error: --fst requires at least two nonempty clusters.')
	
	for i,file in enumerate(os.listdir()):
		if file.endswith('.log'):
			with open(str(file), 'rt') as f:
					lines = f.readlines()
					pops.append(lines[6].strip('  --output/ ').rstrip('\n'))
	
	for i,file in enumerate(os.listdir()):
		if file.endswith('.log'):
			with open(str(file), 'rt') as f:
				for line in f:
						if pattern1.search(line) or pattern2.search(line) != None:
							fst.append(line)
							
	pairwise_fst = list(zip(pops,fst))
	pairwise_fst = pd.DataFrame(pairwise_fst, columns = ['pops','fst'])
	pairwise_fst['fst'] = pairwise_fst['fst'].map(lambda x: x.lstrip('Mean Fst estimate: ').rstrip('\n'))
	pairwise_fst['fst'] = pairwise_fst['fst'].replace('Error: --fst requires at least two nonempty clusters.', 0, regex = True)
	pairwise_fst = pairwise_fst.mask(pairwise_fst.applymap(lambda s: 'End time:' in s if isinstance(s, str) else False))
	pairwise_fst['col_name'] = pairwise_fst['pops'].str.split('.').map(lambda x: x[1])
	pairwise_fst['row_name'] = pairwise_fst['pops'].str.split('.').map(lambda x: x[0])
	pairwise_fst = pairwise_fst.pivot(index='row_name', columns ='col_name', values ='fst')
	pairwise_fst.index.name = None
	pairwise_fst.columns.name = None
	pairwise_fst.to_csv('pairwise_fst.csv', sep = ',')

	clean4 = subprocess.Popen('mkdir PLINK_out', shell = True)
	clean5 = subprocess.Popen('mv *.fst PLINK_out', shell = True)
	clean6 = subprocess.Popen('mv *.log PLINK_out', shell = True)
	clean7 = subprocess.Popen('mv *.clust PLINK_out', shell = True)
	clean8 = subprocess.Popen('mv *.nosex PLINK_out', shell = True)
	clean4.communicate()
	clean5.communicate()
	clean6.communicate()
	clean7.communicate()
	clean8.communicate()

	os.chdir('../')
	make_matrix = subprocess.Popen('Rscript matrix.R', shell = True)
	make_matrix.communicate()
pairwise_fst(prefix)

#Now output a pretty heat map from R!

#To do:
#Make the output quiet
#pipe into the heatmap from R
