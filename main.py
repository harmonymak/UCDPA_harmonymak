import os
import glob
from pycountry_convert import country_alpha3_to_country_alpha2, country_alpha2_to_continent_code
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

# IMPORT DATA

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

# ANALYZE DATA

# Drop columns that are null/NaN
for column in df:
    if df[column].isnull().sum() == df.shape[0]:
        df.drop(column, axis=1, inplace=True)

# Check if all countries have ISO
reporter_country_iso = df.drop_duplicates(['Reporter', 'Reporter ISO'])
print(reporter_country_iso[reporter_country_iso['Reporter ISO'].isna()]['Reporter'])
# 'Other Asia, nes', 'ASEAN'

partner_country_iso = df.drop_duplicates(['Partner', 'Partner ISO'])
print(partner_country_iso[partner_country_iso['Partner ISO'].isna()]['Partner'])
# 'Other Europe, nes', 'Areas, nes', 'Other Asia, nes', 'Other Africa, nes', 'Oceania, nes', 'Bunkers',
# 'Special Categories', 'Free Zones', 'LAIA, nes', 'North America and Central America, nes', 'US Misc. Pacific Isds'
# 'Neutral Zone', 'Br. Antarctic Terr.'

# These are either regions/continents whose data would duplicate with member countries,
# or are very small territories that would have very little trade activities.
# They can be dropped.
drop_reporter = reporter_country_iso[reporter_country_iso['Reporter ISO'].isna()]['Reporter']
drop_partner = partner_country_iso[partner_country_iso['Partner ISO'].isna()]['Partner']
df = df[df.Reporter.isin(drop_reporter) == False]
df = df[df.Partner.isin(drop_partner) == False]

# Map country to continent
country_continent_dict = {}
countries_no_continent = []
unique_countries_iso = pd.unique(df[['Reporter ISO', 'Partner ISO']].values.ravel('K'))

for country in unique_countries_iso:
    try:
        country_continent_dict[country] = country_alpha2_to_continent_code(country_alpha3_to_country_alpha2(country))
    except (KeyError, TypeError):
        countries_no_continent.append(country)
# print(country_continent_dict)

# Investigate why the continent could not be found for some countries
print(countries_no_continent)
# ['EU2', 'ANT', 'SCG', 'TLS', 'WLD', 'ATA', 'UMI', 'ATF', 'PCN', 'VAT', 'ESH', 'SXM']

for country in countries_no_continent:
    print("Reporter: " + country + " - " + df[df['Reporter ISO'] == country]['Reporter'].head(1))
    print("Partner: " + country + " - " + df[df['Partner ISO'] == country]['Partner'].head(1))
# Reporter: EU2 - EU-28
# Reporter: ANT - Neth. Antilles
# Partner: ANT - Neth. Antilles
# Reporter: SCG - Serbia and Montenegro
# Partner: SCG - Serbia and Montenegro
# Reporter: TLS - Timor-Leste
# Partner: TLS - Timor-Leste
# Partner: WLD - World
# Partner: ATA - Antarctica
# Partner: UMI - United States Minor Outlying Islands
# Partner: ATF - Fr. South Antarctic Terr.
# Partner: PCN - Pitcairn
# Partner: VAT - Holy See (Vatican City State)
# Partner: ESH - Western Sahara
# Partner: SXM - Saint Maarten

# 'EU-28' and 'World' are regions and their data would duplicate with member countries. These rows can be dropped.
df = df[df.Reporter != 'EU-28']
df = df[df.Partner != 'World']

# Google the other countries codes to find which continent they are on and add to the dictionary.
# In SA: 'Neth. Antilles' 'Saint Maarten'
country_continent_dict['ANT'] = 'SA'
country_continent_dict['SXM'] = 'SA'

# In EU: 'Serbia and Montenegro' 'Holy See (Vatican City State)'
country_continent_dict['SCG'] = 'EU'
country_continent_dict['VAT'] = 'EU'

# In AS: 'Timor-Leste'
country_continent_dict['TLS'] = 'AS'

# In NA: 'United States Minor Outlying Islands'
country_continent_dict['UMI'] = 'NA'

# In OC: 'Pitcairn'
country_continent_dict['PCN'] = 'OC'

# In AF: 'Western Sahara'
country_continent_dict['ESH'] = 'AF'

# Create new abbreviation for Antarctica AT: 'Antarctica' 'Fr. South Antarctic Terr.'
country_continent_dict['ATA'] = 'AT'
country_continent_dict['ATF'] = 'AT'

# "China, " and " SAR" can be dropped from "China, Hong Kong SAR" and "China, Macau SAR" for simplicity.
df['Reporter'] = [re.sub(r"China\W\s", "", str(country)) for country in df['Reporter']]
df['Reporter'] = [re.sub(r"\sSAR", "", str(country)) for country in df['Reporter']]
df['Partner'] = [re.sub(r"China\W\s", "", str(country)) for country in df['Partner']]
df['Partner'] = [re.sub(r"\sSAR", "", str(country)) for country in df['Partner']]

# Add reporter and partner continent to df and create df_continent for a concise record of continental trade.
df['Reporter Continent'] = df['Reporter ISO'].map(country_continent_dict)
df['Partner Continent'] = df['Partner ISO'].map(country_continent_dict)
df_continent = df.groupby(['Year', 'Reporter Continent', 'Partner Continent', 'Commodity'])[
    'Trade Value (US$)'].sum().reset_index()


# Define function to find total export/import value by a country in a particular year
def trade_value(country, year):
    print(country + "'s trade value in " + str(year) + " in USD")
    print("Export : " + "${:,.0f}".format(
        df.loc[(df['Reporter'] == country) & (df['Year'] == year), 'Trade Value (US$)'].sum()))
    print("Import : " + "${:,.0f}".format(
        df.loc[(df['Partner'] == country) & (df['Year'] == year), 'Trade Value (US$)'].sum()))


# Define function to find export/import value by a country in a particular year, listed by commodities
def trade_value_commodity(country, year):
    print(
        df.assign(
            export_value=np.where((df['Reporter'] == country) & (df['Year'] == year), df['Trade Value (US$)'], 0),
            import_value=np.where((df['Partner'] == country) & (df['Year'] == year), df['Trade Value (US$)'], 0)
        ).groupby('Commodity').agg({'export_value': sum, 'import_value': sum})
    )


# VISUALIZATION

# Plot trade value over time by commodity
g1 = sns.relplot(data=df_continent, x="Year", y="Trade Value (US$)", kind="line", hue="Commodity", ci=None)
g1.fig.suptitle('World Trade Value by Commodity in 2003-2019')
plt.show()

# Plot trade value by commodity exported by each continent in 2019.
df_continent_2019 = df_continent[df_continent['Year'] == 2019]
g2 = sns.catplot(data=df_continent_2019, x="Reporter Continent", y="Trade Value (US$)", kind="bar", hue="Commodity",
                 ci=None)
g2.fig.suptitle('World Export Value by Commodity in 2019')
plt.show()

# MACHINE LEARNING

# From the first visualization, it is observed that "Animal and vegetable oils, fats and waxes" and
# "Beverages and tobacco" have somewhat linear growth over time. Let's try linear regression on these two commodities.
df_oilfatwax = df_continent[df_continent['Commodity'] == 'Animal and vegetable oils, fats and waxes'].drop('Commodity',
                                                                                                           axis=1)
df_bevtob = df_continent[df_continent['Commodity'] == 'Beverages and tobacco'].drop('Commodity', axis=1)

X_oilfatwax = df_oilfatwax.drop('Trade Value (US$)', axis=1)
X_bevtob = df_bevtob.drop('Trade Value (US$)', axis=1)

y_oilfatwax = df_oilfatwax['Trade Value (US$)']
y_bevtob = df_bevtob['Trade Value (US$)']

cat_oilfatwax = pd.get_dummies(X_oilfatwax, drop_first=True)
X_oilfatwax = X_oilfatwax.drop(['Year', 'Reporter Continent', 'Partner Continent'], axis=1)
X_oilfatwax = pd.concat([X_oilfatwax, cat_oilfatwax], axis=1)

cat_bevtob = pd.get_dummies(X_bevtob, drop_first=True)
X_bevtob = X_bevtob.drop(['Year', 'Reporter Continent', 'Partner Continent'], axis=1)
X_bevtob = pd.concat([X_bevtob, cat_bevtob], axis=1)

X_train_oilfatwax, X_test_oilfatwax, y_train_oilfatwax, y_test_oilfatwax = train_test_split(X_oilfatwax, y_oilfatwax,
                                                                                            test_size=0.3,
                                                                                            random_state=42)
X_train_bevtob, X_test_bevtob, y_train_bevtob, y_test_bevtob = train_test_split(X_bevtob, y_bevtob, test_size=0.3,
                                                                                random_state=42)

reg_oilfatwax = LinearRegression()
reg_oilfatwax.fit(X_train_oilfatwax, y_train_oilfatwax)
y_pred_oilfatwax = reg_oilfatwax.predict(X_test_oilfatwax)
print(reg_oilfatwax.score(X_test_oilfatwax, y_test_oilfatwax))

reg_bevtob = LinearRegression()
reg_bevtob.fit(X_train_bevtob, y_train_bevtob)
y_pred_bevtob = reg_bevtob.predict(X_test_bevtob)
print(reg_bevtob.score(X_test_bevtob, y_test_bevtob))

# Cross validation

cv_results_oilfatwax = cross_val_score(reg_oilfatwax, X_oilfatwax, y_oilfatwax, cv=5)
print(cv_results_oilfatwax)
print(np.mean(cv_results_oilfatwax))

cv_results_bevtob = cross_val_score(reg_bevtob, X_bevtob, y_bevtob, cv=5)
print(cv_results_bevtob)
print(np.mean(cv_results_bevtob))

# The score is so low that there is no point in doing hyperparameter tuning.
# Rescaling the y-axis scale gives a better picture why: the trade value of these two commodities do not follow a
# linear pattern after all.
# There are so many factors that affect world trade, and without adding those factors to the dataset,
# no algorithm in the world will be able to raise the score.
g3 = sns.relplot(data=df_continent, x="Year", y="Trade Value (US$)", kind="line", hue="Commodity", ci=None)
g3.fig.suptitle('World Trade Value by Commodity in 2003-2019 (Rescaled)')
plt.ylim(0, 4000000000)
plt.show()
