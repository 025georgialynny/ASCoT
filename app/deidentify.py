import pandas as pd
import numpy as np
import requests
import time
import re
from tqdm import tqdm

samp_data = pd.read_csv("data/original_data/RGC_trial_RoR_042522.csv")



for id in np.unique(samp_data.mrn): 
    samp_data.mrn = samp_data.mrn.replace(id, np.random.randint(1000000, 9999999))

for id in np.unique(samp_data.btid): 
    samp_data.btid = samp_data.btid.replace(id, np.random.randint(10000000, 99999999))

race_list = samp_data.race.unique()
sex_list = samp_data.sex.unique()
eth_list = samp_data.ethnicity.unique()


race_dict = {}
for id in np.unique(samp_data.mrn):
    race_dict[id] = np.random.choice(race_list)


samp_data.race = samp_data.mrn.map(race_dict)

sex_dict = {}
for id in np.unique(samp_data.mrn):
    sex_dict[id] = np.random.choice(sex_list)


samp_data.sex = samp_data.mrn.map(sex_dict)

eth_dict = {}
for id in np.unique(samp_data.mrn):
    eth_dict[id] = np.random.choice(eth_list)

samp_data.ethnicity = samp_data.mrn.map(eth_dict)

rsid_dat = pd.read_csv("/com.docker.devenvironments.code/app/data/original_data/Regeneron_HIPV_RGC_freeze1_ACMG_clinvar_list.txt", sep = '\t')

rsid_dat = rsid_dat.iloc[:, 0:-1].drop_duplicates()

rsid_new = []
clnhgvs = []
cdot = []
pdot = []
nmvals = []

links = []

for idx, row in tqdm(samp_data.iterrows()):
    bp = row.hg38
    gene = row.gene
    correct_data = rsid_dat[rsid_dat.BP == bp][rsid_dat.GENE == gene]
    rsid_new.append("rs" + correct_data.rsID.values[0])
    clnhgvs.append(correct_data.CLNHGVS.values[0])
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=" + correct_data.rsID.values[0] +  "[position]&retmode=json")
    aldata = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=" + response.json()['esearchresult']['idlist'][0] + "&retmode=json")
    try: 
        cd, pdo = aldata.json()["result"][response.json()['esearchresult']['idlist'][0]]['title'].split(" ")
    except: 
        cd = aldata.json()["result"][response.json()['esearchresult']['idlist'][0]]['title']
        pdo = ""
    nmnum, cd = cd.split(":")
    cdot.append(cd)
    pdot.append(pdo)
    nmvals.append(re.sub(r'\(.*\)', '', nmnum))
    links.append( response.json()['esearchresult']['idlist'][0] )
    time.sleep(.3)

samp_data['rsid'] = rsid_new
samp_data['CLNHGVS'] = clnhgvs
samp_data["cdot"] = cdot
samp_data["pdot"] = [x.strip("()") for x in pdot] 
samp_data["clinvar"] = links
samp_data["NM"] = nmvals


samp_data.to_csv("data/samples/RGC_trial_RoR_042522/sample_data.csv")