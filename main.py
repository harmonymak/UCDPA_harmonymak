# IMPORT DATA

import os
import glob
import pandas as pd

# Import csv files into one data frame
year = 2003
df = pd.DataFrame()
while year <= 2019:
    path = "C:/Users/user/PycharmProjects/UCDPA_harmonymak/data/" + str(year)
    files = glob.glob(os.path.join(path, "*.csv"))
    for f in files:
        csv = pd.read_csv(f, header=0)

        # Some files don't have data because these countries are too small, are in war, doesn't exist anymore
        # or for whatever reason does not report its trade data to the UN.
        # These countries' file only has the header row and contain the text
        # "No data matches your query or your query is too complex. Request JSON or XML format for more information."
        # They don't need to be added to the data frame.
        if csv.shape[0] > 2:
            df = df.append(csv)
    year += 1
