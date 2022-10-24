import pandas as pd 

primer = pd.read_csv("/com.docker.devenvironments.code/app/data/samples/RGC_trial_RoR_042522/primer_list.csv")

split_details = primer.primer_details.str.split("-", expand = True)

for row in range(len(split_details)):
     if split_details.iloc[row,3] == None:
             split_details.iloc[row,3] = split_details.iloc[row,2]
             split_details.iloc[row,2] = 0
     else:
             split_details.iloc[row, 2] = 1



split_details.columns = ["gene", "pnum", "M13", "direction"]

for col in split_details.columns:
     primer[col] = split_details[col]


primer.to_csv("/com.docker.devenvironments.code/app/data/samples/RGC_trial_RoR_042522/primer_list.csv", index=False)