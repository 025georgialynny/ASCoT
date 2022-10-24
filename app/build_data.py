#!/usr/bin/env python3
import sys
import re
import os
import json
import pandas as pd
import time

def make_data():
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basedir= os.path.join(sys._MEIPASS, "app")
    except Exception:
        basedir = os.path.join(os.path.abspath("."), "app")

    write_logs = False
    database = json.load(open(os.path.join(basedir, 'database_outline.json')))


    for tables, vname in database["tables"].items():
        column_list = ""
        for colnames in database["table_mapping"][tables]["variables"]:
            column_list = column_list + "\"" + colnames + "\","
        clist = eval(column_list)
        print(vname)
        print(pd.DataFrame(columns = clist))
        exec(vname + " = pd.DataFrame(columns = clist)", locals(), globals())
        eval(vname)

    print("LOCALS")
    print([[key] for key, val in locals().items()])
    print("GLOBALS")


    omim_duplicates = []

    for folders in os.listdir(os.path.join(basedir, 'data', 'samples')):
        write_logs = False
        folder_files = os.listdir(os.path.join(basedir, 'data', 'samples', folders))
        for tables,vname in  database["tables"].items():
            if vname + ".csv" not in folder_files:
                if vname == "logs":
                    write_logs = True
                    continue
                if vname == "samples_overview" and "sample_data.csv" in folder_files:
                    write_logs = True
                    base_df = pd.read_csv(os.path.join(basedir, 'data', 'samples', folders, "sample_data.csv"))
                    base_df.insert(0, "sample_name", [str(base_df.loc[x, "variant"])  + "_" + str(base_df.loc[x, "mrn"]) + "_" + str(base_df.loc[x, "instrumentid"]) for x in range(len(base_df))])
                    
                    for sample_id in base_df['sample_name']: 
                        if sample_id in list(base_df.sample_name[base_df.duplicated()]):
                            print("Error: sample " + sample_id + " duplicated in data file. Only keeping first instance", file = sys.stderr)
                            if sample_id not in list(logs.sample_name[logs.action == "uploaded"]):
                                logs.loc[len(logs)] = ['global', time.time(), "uploaded", "",sample_id, ""]
                            else:
                                logs.loc[len(logs)] = ['global', time.time(), "uploaded", "skipping duplicate sample",sample_id+"-duplicate", ""]
                        elif sample_id in list(base_df.sample_name[base_df.sample_name.duplicated()]):
                            if sample_id not in list(logs.sample_name[logs.action == "uploaded"]):
                                print("Error: sample " + sample_id + " duplicated in data file but data isn't the same. Only keeping first instance", file = sys.stderr)
                                logs.loc[len(logs)] = ['global', time.time(), "uploaded", "",sample_id, ""]
                                sample_df = base_df[base_df.sample_name == sample_id ]
                                for cname in base_df.columns:
                                    bool_list = ~sample_df[cname].duplicated()
                                    if cname == "OMIM_Phenotype":
                                        print("\t NOTE: sample " + sample_id + " merging OMIM_Phenotype", file = sys.stderr)                    
                                        logs.loc[len(logs)] = ['global', time.time(), "merged OMIM_Phenotype", "",sample_id, ""]
                                        omim_duplicates.append(sample_id)
                                        continue
                                    sample_colsubset = sample_df.loc[bool_list, cname]
                                    if (len(sample_colsubset) > 1) and (cname != "OMIM_Phenotype"):
                                        print("Unique Entries in column" + cname)
                                        print(sample_df.loc[bool_list, ])

                            else:
                                logs.loc[len(logs)] = ['global', time.time(), "uploaded",  "skipping duplicate sample - NOTE DISCREPANCIES IN COLUMNS",sample_id+"-duplicate",""]
                        else: 
                            logs.loc[len(logs)] = ['global', time.time(), "uploaded", "",sample_id, ""]
                    base_df['OMIM_Phenotype'] = base_df.groupby(['sample_name'])['OMIM_Phenotype'].transform(lambda x : '|'.join(x))
                    sample_data = base_df.drop_duplicates(subset = ['sample_name'])
                    globals()["samples_overview"] = pd.merge(left = sample_data, right = samples_overview, how = "outer")
                exec(vname + ".to_csv('" + os.path.join(basedir, 'data', 'samples', folders, vname + ".csv")+ "', index = False)")
        if write_logs:
            logs.to_csv(os.path.join(basedir, 'data', 'samples', folders, "logs.csv") , index = False)


if __name__ == '__main__':
    make_data()

