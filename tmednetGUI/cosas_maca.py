from os.path import isfile, join

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from os import listdir
from pathlib import Path
import zipfile

from matplotlib.lines import Line2D

# Directori amb zips
input_dirs = ["../src/input_files/Subidos/", "../src/input_files/costa/"]
for input_dir in input_dirs:
    dir_files = [f for f in listdir(input_dir) if isfile(join(input_dir, f))]

    # DataFrame final buit
    df_total = pd.DataFrame()

    # Bucle per tots els ZIP del directori
    for file in dir_files:
        zip_df = pd.read_csv(input_dir + file, sep='\t')
        df_total = pd.concat([df_total, zip_df], ignore_index=True)

    # ✔ Convertir columna Date a datetime (si cal)
    if "Date" in df_total.columns:
        df_total["Date"] = pd.to_datetime(df_total["Date"], errors="coerce")

    # fa la mitjana de cada fitxer
    df_means = df_total.groupby('Date', as_index=False).mean(numeric_only=True)
    df_means['year'] = df_means['Date'].dt.year

    sns.lineplot(data=df_means, x="year", y="5")
plt.xlabel('Año')
plt.ylabel('Temperatura media (ºC)')

legend_handles = [Line2D([], [], color='blue', label='Mediterraneo', ls='-'),
                  Line2D([], [], color='orange', label='Catalan', ls='-')]
plt.legend(handles=legend_handles)
plt.savefig("mediterranean and catalan_yearly_v2.png")


print("Fet! Fitxer generat:")



'''df = pd.read_csv("../src/input_files/Database_T_06_Medes_200207-202510.txt", sep='\t')
cols = df.columns[2:]
df['year'] = pd.to_datetime(df['Date']).dt.year
df['Date'] = pd.to_datetime(df['Date'])
years = df['year'].unique()

daily_df = df.groupby('Date')[cols].mean().reset_index()
daily_df['year'] = daily_df['Date'].dt.year
"""for col in cols:
    p01, p99 = df[col].quantile([0.01, 0.99])
    df = df[(df[col] >= p01) & (df[col] <= p99)]

"""
sns.lineplot(data=daily_df, x="year", y="5")
plt.xlabel('Year')
plt.ylabel('Mean Temperature (ºC)')
plt.savefig("medes_yearly.png")
print('hey')
'''