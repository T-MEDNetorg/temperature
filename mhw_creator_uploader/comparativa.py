import pandas as pd
import numpy as np

df_odmclimate = pd.read_excel("C:/Users/marcj/Documents/CSIC/OdM/Verificació Quim/Mortality_ODMCLIMATE.xlsx", sheet_name="Hoja1")
df_quim = pd.read_csv("C:/Users/marcj/Documents/CSIC/OdM/Verificació Quim/Mortality_QUIM.csv", sep=',')

cols_com = df_odmclimate.columns.intersection(df_quim.columns)
totes_incloses = df_odmclimate[cols_com[:-1]].merge(df_quim[cols_com[:-1]], how='left', indicator=True)['_merge'].eq('both').all()

no_in_df2 = df_odmclimate.merge(df_quim[cols_com[:-1]], how='left', indicator=True).query('_merge == "left_only"').drop(columns='_merge')

import pandas as pd

# 1️⃣ Llegim dades
df_odmclimate = pd.read_excel("C:/Users/marcj/Documents/CSIC/OdM/Verificació Quim/Mortality_ODMCLIMATE.xlsx", sheet_name="Hoja1")
df_quim = pd.read_csv("C:/Users/marcj/Documents/CSIC/OdM/Verificació Quim/Mortality_QUIM.csv", sep=',')

# 2️⃣ Ens quedem només amb les columnes comunes
cols_com = df_odmclimate.columns.intersection(df_quim.columns)
cols_com = cols_com.sort_values()

df1 = df_odmclimate[cols_com].copy()
df2 = df_quim[cols_com].copy()

# 3️⃣ Afegim una columna temporal d’identificador únic per fila
# (per poder comparar sense dependre de l'índex)
df1["_row_id"] = range(len(df1))
df2["_row_id"] = range(len(df2))

# 4️⃣ Fem un merge "outer" per veure on hi ha coincidències i diferències
merged = df1.merge(df2, how="outer", on=cols_com.tolist(), indicator=True)

# 5️⃣ Files que no són a df2
no_in_df2 = merged.query('_merge == "left_only"').drop(columns="_merge")

print(f"{len(no_in_df2)} files de df_odmclimate no són a df_quim")

# 6️⃣ Per veure *per què* no són iguals:
# Busquem coincidències parcials per fila
def compara_files(row, df_ref, cols):
    """
    Compara una fila amb el df_ref per trobar quines columnes no coincideixen.
    """
    coincidencies = []
    for col in cols:
        if row[col] in df_ref[col].values:
            coincidencies.append(col)
    return coincidencies

no_in_df2["columnes_que_coincideixen"] = no_in_df2.apply(lambda r: compara_files(r, df_quim, cols_com), axis=1)

# També podem veure quines *no* coincideixen
no_in_df2["columnes_diferents"] = no_in_df2.apply(
    lambda r: [c for c in cols_com if c not in r["columnes_que_coincideixen"]], axis=1
)

print(no_in_df2[["columnes_que_coincideixen", "columnes_diferents"]].head())

print(totes_incloses)
print("pe")