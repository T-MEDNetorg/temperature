import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import data_manager as dm
from scipy.ndimage.filters import uniform_filter1d


# Función para aplicar el filtro solo a los bloques de datos continuos
def filter_running_average(series, size):
    # Inicializamos una lista para almacenar los resultados
    result = np.nan * np.ones_like(series)

    # Iteramos sobre los segmentos de datos no NaN
    start_idx = None
    for i in range(len(series)):
        if not np.isnan(series[i]) and start_idx is None:
            start_idx = i  # Inicio de un nuevo bloque de datos
        elif np.isnan(series[i]) and start_idx is not None:
            # Fin de un bloque de datos
            result[start_idx:i] = uniform_filter1d(series[start_idx:i], size=size)
            start_idx = None  # Fin del bloque
    # Si la serie termina con datos no NaN, aplicamos el filtro al último bloque
    if start_idx is not None:
        result[start_idx:] = uniform_filter1d(series[start_idx:], size=size)

    return result


# Daily temperature range plot
df = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202510.txt', sep='\t')
df['Date'] =  pd.to_datetime(df['Date'], dayfirst=True)
df['Season'] = df['Date'].dt.quarter

df_2021 = df.loc[(df['Date'].dt.year == 2021)]

cols = ['15', '40']

for col in cols:
    p01, p99 = df_2021[col].quantile([0.01, 0.99])
    df_2021 = df_2021[(df_2021[col] >= p01) & (df_2021[col] <= p99)]
    p01, p99 = df[col].quantile([0.01, 0.99])
    df = df[(df[col] >= p01) & (df[col] <= p99)]

daily_mean = df_2021.groupby('Date')[cols].mean().reset_index()

# --- 4️⃣ Calcular la variació diària (diferència respecte al dia anterior) ---
daily_var = daily_mean.copy()
daily_var[cols] = daily_mean[cols].diff()

# --- 5️⃣ Representar amb seaborn ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=daily_var, x='Date', y='15', label='15 m', color='#d4a19d')
sns.lineplot(data=daily_var, x='Date', y='40', label='40 m', color='#84cbec')

plt.title('Daily variation - 2021')
plt.xlabel('Date')
plt.ylabel('Variació de temperatura (°C)')
plt.legend(title='Fondària')
plt.grid(True)
plt.tight_layout()
plt.show()

# --- 3️⃣ Calcular la variació diària (max - min) per cada fondària ---
daily_range = (
    df_2021.groupby('Date')[cols]
    .agg(lambda x: x.max() - x.min())
    .reset_index()
)

daily_range_whole = (
    df.groupby('Date')[cols]
    .agg(lambda x: x.max() - x.min())
    .reset_index()
)

daily_range_whole['day_of_year'] = daily_range_whole['Date'].dt.dayofyear


# --- 4️⃣ Gràfica amb seaborn ---
plt.figure(figsize=(12, 6))
sns.lineplot(data=daily_range, x='Date', y='15', label='15 m')
sns.lineplot(data=daily_range, x='Date', y='40', label='40 m')

plt.title('Daily Amplitude (Tmax - Tmin) - 2021')
plt.xlabel('Date')
plt.ylabel('Variació diària de temperatura (°C)')
plt.legend(title='Fondària')
plt.grid(True)
plt.tight_layout()
plt.show()

# --- 4️⃣ Afegir la tendència (mitjana mòbil de 7 dies) ---
window_size = 7  # pots provar 14 si vols més suavitat
for col in cols:
    daily_range[f'{col}_trend'] = daily_range[col].rolling(window=window_size, center=True).mean()

# --- 5️⃣ Visualització amb seaborn ---
plt.figure(figsize=(12, 6))

# Línies originals (amplitud diària)
sns.lineplot(data=daily_range, x='Date', y='15', label='15 m (diari)', alpha=0.3)
sns.lineplot(data=daily_range, x='Date', y='40', label='40 m (diari)', alpha=0.3)

# Línies de tendència (suavitzades)
sns.lineplot(data=daily_range, x='Date', y='15_trend', label='Tendència 15 m', linewidth=2)
sns.lineplot(data=daily_range, x='Date', y='40_trend', label='Tendència 40 m', linewidth=2)

plt.title('Amplitud tèrmica diària i tendència - 2021')
plt.xlabel('Data')
plt.ylabel('Variació diària de temperatura (°C)')
plt.legend(title='Fondària')
plt.grid(True)
plt.tight_layout()
plt.show()


# --- 4️⃣ Calcular la tendència lineal amb np.polyfit ---
# Convertim la data a un número (dies des de l’inici)
x = (daily_range['Date'] - daily_range['Date'].min()).dt.days

for col in cols:
    m, b = np.polyfit(x, daily_range[col], 1)  # ajust lineal: y = m*x + b
    daily_range[f'{col}_trend_line'] = m * x + b
    print(f"Tendència {col}: pendent = {m:.5f} °C/dia")  # info útil

# --- 5️⃣ Gràfica ---
plt.figure(figsize=(12, 6))

# Dades originals
sns.lineplot(data=daily_range, x='Date', y='15', label='15 m (diari)', alpha=0.4)
sns.lineplot(data=daily_range, x='Date', y='40', label='40 m (diari)', alpha=0.4)

# Tendències lineals
sns.lineplot(data=daily_range, x='Date', y='15_trend_line', label='Tendència lineal 15 m', linewidth=2)
sns.lineplot(data=daily_range, x='Date', y='40_trend_line', label='Tendència lineal 40 m', linewidth=2)

plt.title('Amplitud tèrmica diària i tendència lineal - 2021')
plt.xlabel('Data')
plt.ylabel('Variació diària de temperatura (°C)')
plt.legend(title='Fondària')
plt.grid(True)
plt.tight_layout()
plt.show()

# --- 4️⃣ Calcular la tendència lineal amb np.polyfit ---
# Convertim la data a un número (dies des de l’inici)
x = (daily_range_whole['Date'] - daily_range_whole['Date'].min()).dt.days

for col in cols:
    m, b = np.polyfit(x, daily_range_whole[col], 1)  # ajust lineal: y = m*x + b
    daily_range_whole[f'{col}_trend_line'] = m * x + b
    print(f"Tendència {col}: pendent = {m:.5f} °C/dia")  # info útil

mean_annual_cycle = daily_range_whole.groupby('day_of_year')[cols].mean().reset_index()
trend_annual_cycle = daily_range_whole.groupby('day_of_year')[[f'{col}_trend_line' for col in cols]].mean().reset_index()

plt.figure(figsize=(12, 6))

sns.lineplot(data=mean_annual_cycle, x='day_of_year', y='15', label='15 m (mitjana diària)', alpha=0.4)
sns.lineplot(data=mean_annual_cycle, x='day_of_year', y='40', label='40 m (mitjana diària)', alpha=0.4)

# Tendència lineal mitjana (opcional, pot ser poc significativa a escala anual)
sns.lineplot(data=trend_annual_cycle, x='day_of_year', y='15_trend_line', label='Tendència lineal 15 m', linewidth=2)
sns.lineplot(data=trend_annual_cycle, x='day_of_year', y='40_trend_line', label='Tendència lineal 40 m', linewidth=2)

plt.title('Cicle anual mitjà i tendència lineal (2002–2025)')
plt.xlabel('Dia de l’any')
plt.ylabel('Amplitud tèrmica diària (°C)')
plt.legend(title='Fondària')
plt.grid(True)
plt.tight_layout()
plt.show()


# --- 🔥 Nou plot: Distribució de la variació diària a l'estiu ---

# Definim l'estiu (jas o trimestre 3 si uses df['Season'])
summer = df_2021[df_2021['Date'].dt.month.isin([7, 8, 9])]

# Recalculem l'amplitud diària per a l'estiu
daily_range_summer = (
    summer.groupby('Date')[cols]
    .agg(lambda x: x.max() - x.min())
    .reset_index()
)

# Round to neares integer
#daily_range_summer = daily_range_summer.round()
# --- Fem un histograma (freqüència de dies per amplitud) ---
plt.figure(figsize=(10, 6))

bins = np.arange(0, round(daily_range_summer[['15','40']].values.max()), 1)

for col, color in zip(cols, ['#d4a19d', '#84cbec']):
    sns.histplot(
        data=daily_range_summer,
        x=col,
        bins=bins,            # pots ajustar segons la resolució que vulguis
        kde=False,          # no afegim corba de densitat
        color=color,
        stat='density',
        alpha=0.6,
        label=f'{col} m'
    )

plt.title('Distribució de la variació diària de temperatura a l’estiu (2021)')
plt.xlabel('Variació diària de temperatura (°C)')
plt.ylabel('Densitat (proporció) de dies')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# --- Creem les categories per rangs de temperatura ---
ranges = [
    (13, 20, "13–20 °C"),
    (20, 25, "20–25 °C")
]

daily_summer = summer.groupby('Date')[cols].mean()

# Funció auxiliar per classificar cada valor
def classify_range(value):
    for lower, upper, label in ranges:
        if lower <= value < upper:
            return label
    return None  # fora del rang


for col, color in zip(cols, ['#d4a19d', '#84cbec']):
    # Classifica cada dia segons el rang corresponent
    daily_summer[f'{col}_range'] = daily_summer[col].apply(classify_range)

    # Comptem la freqüència de dies per cada rang
    freq = daily_summer[f'{col}_range'].value_counts().reindex([r[2] for r in ranges])

    # Fem el barplot
    sns.barplot(
        x=freq.index,
        y=freq.values,
        color=color,
        alpha=0.6,
        label=f'{col} m'
    )

plt.title('Freqüència de dies segons mitjana diària d’estiu (2021)')
plt.xlabel('Rang de mitjana diària (°C)')
plt.ylabel('Freqüència de dies')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# Passem a format llarg (long) per poder fer barres separades per fondària

df_long = pd.melt(
    daily_summer.reset_index(),
    id_vars=['Date'],
    value_vars=[f'{col}_range' for col in cols],
    var_name='Depth',
    value_name='Range'
)

# Netejem el nom de fondària (de "15_range" → "15 m")
df_long['Depth'] = df_long['Depth'].str.replace('_range', ' m')

# Comptem la freqüència per combinació (rang, fondària)
freq = df_long.groupby(['Range', 'Depth']).size().reset_index(name='Count')

# Assegurem l'ordre dels rangs
freq['Range'] = pd.Categorical(freq['Range'], categories=[r[2] for r in ranges], ordered=True)

# --- Barplot amb barres costat a costat ---
plt.figure(figsize=(8, 6))
sns.barplot(
    data=freq,
    x='Range',
    y='Count',
    hue='Depth',
    palette=['#d4a19d', '#84cbec']
)

plt.title('Freqüència de dies segons variació diària d’estiu (2021)')
plt.xlabel('Rang de variació diària (°C)')
plt.ylabel('Freqüència de dies')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# Recalculem l'amplitud diària per a l'estiu
daily_range_summer = (
    summer.groupby('Date')[cols]
    .agg(lambda x: x.max() - x.min())
    .reset_index()
)

# Definim bins d'1 °C (ajusta el màxim si vols més marge)
max_val = np.ceil(daily_range_summer[cols].values.max())
bins = np.arange(0, max_val + 2, 3)

# Assignem cada valor al seu interval
for col in cols:
    daily_range_summer[f'{col}_bin'] = pd.cut(
        daily_range_summer[col],
        bins=bins,
        right=False,
        labels=[f"{int(b)}–{int(b+3)}" for b in bins[:-1]]
    )

# Convertim a format llarg per poder fer barres costat a costat
df_long = pd.melt(
    daily_range_summer,
    id_vars=['Date'],
    value_vars=[f'{col}_bin' for col in cols],
    var_name='Depth',
    value_name='Range'
)

# Neteja de noms (de "15_bin" → "15 m")
df_long['Depth'] = df_long['Depth'].str.replace('_bin', ' m')

# Comptem la freqüència per cada combinació (rang, fondària)
freq = df_long.groupby(['Range', 'Depth']).size().reset_index(name='Count')

# Elimina valors buits (pot passar si algun dia no té dada dins dels bins)
freq = freq.dropna(subset=['Range'])

# Assegurem ordre dels rangs
freq['Range'] = pd.Categorical(freq['Range'], categories=[f"{int(b)}–{int(b+3)}" for b in bins[:-1]], ordered=True)

# --- Barplot costat a costat ---
plt.figure(figsize=(12, 6))
sns.barplot(
    data=freq,
    x='Range',
    y='Count',
    hue='Depth',
    palette=['#d4a19d', '#84cbec']
)

plt.title('Distribució de la variació diària de temperatura a l’estiu (2021)')
plt.xlabel('Rang de variació diària (°C)')
plt.ylabel('Freqüència de dies')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


#summer
#summer = df[df['Date'].dt.month.isin([7, 8, 9])]
#start of summer
summer = df[df['Date'].dt.month.isin([5,6])]
summer['day_month'] = summer['Date'].dt.strftime("2000-%m-%d")
daily_summer = summer.groupby('day_month')[cols].mean()

for col, color in zip(cols, ['#d4a19d', '#84cbec']):
    # Classifica cada dia segons el rang corresponent
    daily_summer[f'{col}_range'] = daily_summer[col].apply(classify_range)

#daily_summer.index = daily_summer.index.astype(str)

# Passem a format llarg (long) per poder fer barres separades per fondària

df_long_whole = pd.melt(
    daily_summer.reset_index(),
    id_vars=['day_month'],
    value_vars=[f'{col}_range' for col in cols],
    var_name='Depth',
    value_name='Range'
)

# Netejem el nom de fondària (de "15_range" → "15 m")
df_long_whole['Depth'] = df_long_whole['Depth'].str.replace('_range', ' m')

# Comptem la freqüència per combinació (rang, fondària)
freq = df_long_whole.groupby(['Range', 'Depth']).size().reset_index(name='Count')

# Assegurem l'ordre dels rangs
freq['Range'] = pd.Categorical(freq['Range'], categories=[r[2] for r in ranges], ordered=True)

# --- Barplot amb barres costat a costat ---
plt.figure(figsize=(8, 6))
sns.barplot(
    data=freq,
    x='Range',
    y='Count',
    hue='Depth',
    palette=['#d4a19d', '#84cbec']
)

plt.title('Freqüència de dies segons variació diària d’estiu (2002-2025)')
plt.xlabel('Rang de variació diària (°C)')
plt.ylabel('Freqüència de dies')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

# Recalculem l'amplitud diària per a l'estiu
daily_range_summer = (
    summer.groupby('Date')[cols].agg(lambda x: x.max() - x.min()).reset_index()
)

daily_range_summer['year'] = daily_range_summer['Date'].dt.year

daily_range_summer['day_month'] = daily_range_summer['Date'].dt.strftime("2000-%m-%d")

#daily_range_summer = daily_range_summer.groupby('day_month').mean()
#daily_range_summer = daily_range_summer.drop('Date', axis=1).reset_index()
# Definim bins d'1 °C (ajusta el màxim si vols més marge)
max_val = np.ceil(daily_range_summer[cols].values.max())
bins = np.arange(0, max_val + 1, 1)
#TODO opcio per contar
#daily_range_summer.groupby('15_bin').count()

# Assignem cada valor al seu interval
for col in cols:
    daily_range_summer[f'{col}_bin'] = pd.cut(
        daily_range_summer[col],
        bins=bins,
        right=False,
        labels=[f"{int(b)}–{int(b+1)}" for b in bins[:-1]]
    )
# Convertim a format llarg
df_long = pd.melt(
    daily_range_summer,
    id_vars=['Date','year'],
    value_vars=[f'{col}_bin' for col in cols],
    var_name='Depth',
    value_name='Range'
)

df_long['Depth'] = df_long['Depth'].str.replace('_bin',' m')

# Comptem el número de dies per any, rang i fondària
df_counts = df_long.groupby(['year','Depth','Range']).size().reset_index(name='Count')

# Calculem mitjana i desviació anual per cada rang i fondària
stats = df_counts.groupby(['Depth','Range']).agg(
    Mean=('Count','mean'),
    Std=('Count','std')
).reset_index()

# Llista dels rangs i fondàries
ranges = stats['Range'].unique()
depths = ['15 m', '40 m']
width = 0.35  # amplada de cada barra
x = np.arange(len(ranges))  # posició de cada rang

plt.figure(figsize=(12,6))

for i, depth in enumerate(depths):
    subset = stats[stats['Depth']==depth]
    plt.bar(
        x + i*width - width/2,  # desplaçament per posar-les costat a costat
        subset['Mean'],
        yerr=subset['Std'],
        width=width,
        alpha=0.6,
        color='#d4a19d' if depth=='15 m' else '#84cbec',
        label=depth,
        capsize=5
    )

plt.title('Número de dies mitjà per any segons rang de variació (Maig Juny) - Medes')
plt.xlabel('Rang de variació diària (°C)')
plt.ylabel('Nombre de dies (mitjana anual)')
plt.legend(title='Fondària')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()


print('Plot done')























df = pd.read_csv('../src/input_files/Database_T_06_Medes_200207-202510.txt', sep='\t')
df['Date'] =  pd.to_datetime(df['Date'], dayfirst=True)
df['Season'] = df['Date'].dt.quarter

# Media diaria de 2021 a 15m
df_year = df.loc[(df['Date'].dt.year == 2021)]
#Filtro a 15 dias running
df_filtered = pd.DataFrame({'15': uniform_filter1d(df_year['15'], size=360), '40': uniform_filter1d(df_year['40'], size=360)}, index=df_year['Date'])
df_diario = df_filtered.groupby(df_filtered.index.date).mean()

df_diario.plot(color=['#d4a19d', '#84cbec'])
plt.title('2021 temperature at 15 and 40m')
plt.clf()
# Media diaria de 2021 a 15m
df_year = df.loc[(df['Date'].dt.year == 2021)]
#Filtro a 15 dias running
df_filtered = pd.DataFrame({'15': uniform_filter1d(df_year['15'], size=360), '40': uniform_filter1d(df_year['40'], size=360)}, index=df_year['Date'])
df_diario = df_filtered.groupby(df_filtered.index.date).mean()

#Para std
ugh = df_filtered.resample('D')
ugh = ugh.agg(['mean', 'std'])# Para tener en cuenta los outliers
#df_new = pd.DataFrame({'15': df_year['15'].groupby(df_year['Date']).mean(), '40': df_year['40'].groupby(df_year['Date']).mean()}, index=df_year['Date'])
#df_diario = df_new.groupby(df_new.index.date).mean()
df_diario_mean = df_diario.mean()
df_diario_std = df_diario.std()
df_diario.plot(color=['#d4a19d', '#84cbec'])
plt.title('2021 temperature at 15 and 40m')
plt.savefig('../src/output_images/2021_temp 15 and 40')

plt.clf()
achis = ugh.loc[:, pd.IndexSlice[:, 'std']]
achis.plot(color=['#d4a19d', '#84cbec'], label=['15', '40'])
plt.title('2021 standard deviation at 15 and 40m')
plt.legend(title='Depth')
plt.savefig('../src/output_images/2021_std 15 and 40')
plt.clf()

df_year_5mean = df.loc[(df['Date'].dt.year >= 2002) & (df['Date'].dt.year <= 2024)]
df_filtered_5mean = pd.DataFrame({'15': uniform_filter1d(df_year_5mean.groupby(df['Date'].dt.strftime('%m-%d'))['15'].mean(), size=15), '40': uniform_filter1d(df_year_5mean.groupby(df['Date'].dt.strftime('%m-%d'))['40'].mean(), size=15)}, index=df_year_5mean.groupby(df['Date'].dt.strftime('%m-%d'))['15'].mean().index)
df_filtered_5mean.plot(color=['#d4a19d', '#84cbec'])

# Para tener en cuenta los outliers
#df_new_5 = pd.DataFrame({'15': df_year_5mean.groupby(df['Date'].dt.strftime('%m-%d'))['15'].mean(), '40':df_year_5mean['40'].groupby(df_year_5mean['Date']).mean()}, index=df_year_5mean.groupby(df['Date'].dt.strftime('%m-%d'))['15'].mean().index)
#df_new_5.plot(color=['#d4a19d', '#84cbec'])
plt.title('2002-2024 temperature at 15 and 40m')
plt.savefig('../src/output_images/2002-2024_temp 15 and 40')
plt.clf()
'''
mask = ~np.isnan(df_year_5mean['15'])

# Filtrar solo los valores no NaN
filtered_values = uniform_filter1d(df_year_5mean['15'][mask], size=360)

# Crear un array de salida con NaN en las posiciones originales
df_year_5mean['15_filtered'] = np.nan
df_year_5mean['15_filtered'][mask] = filtered_values

mask = ~np.isnan(df_year_5mean['40'])

# Filtrar solo los valores no NaN
filtered_values = uniform_filter1d(df_year_5mean['40'][mask], size=360)

# Crear un array de salida con NaN en las posiciones originales
df_year_5mean['40_filtered'] = np.nan
df_year_5mean['40_filtered'][mask] = filtered_values

df_year_5mean['Date'] = df_year_5mean['Date'].dt.strftime('%m-%d')
df_year_5mean['Date'] = pd.to_datetime('2000-' + df_year_5mean['Date'], format='%Y-%m-%d')
'''
'''
df_year_5mean['15_filled'] = df_year_5mean['15'].fillna(df_year_5mean['15'].mean())
df_year_5mean['40_filled'] = df_year_5mean['15'].fillna(df_year_5mean['40'].mean())

# Aplicar el filtro sobre la serie sin NaN
df_year_5mean['15_filtered'] = uniform_filter1d(df_year_5mean['15_filled'], size=360)
df_year_5mean['40_filtered'] = uniform_filter1d(df_year_5mean['40_filled'], size=360)'''
df_year_5mean.set_index('Date', inplace=True)
df_year_5mean['15_filtered'] = filter_running_average(df_year_5mean['15'], size=360)
df_year_5mean['40_filtered'] = filter_running_average(df_year_5mean['40'], size=360)

haha = df_year_5mean[['15_filtered', '40_filtered']]
haha.index = haha.index.map(lambda x: x.replace(year=2000))
ugh = haha.resample('D')
ugh = ugh.agg(['mean', 'std'])# Para tener en cuenta los outliers

achis = ugh.loc[:, pd.IndexSlice[:, 'std']]
achis.index = achis.index.strftime('%m-%d')
ax = achis.plot(color=['#d4a19d', '#84cbec'])
handles, labels = ax.get_legend_handles_labels()

# Filtrar las etiquetas y los handles de la leyenda según las etiquetas que tú quieras
labels = ['15', '40']  # Aquí solo le pones las etiquetas que deseas mostrar en la leyenda

# Asignar la leyenda con los nuevos labels
ax.legend(handles[:2], labels, title="Depth", loc="best")
plt.title('2002-2024 standard deviation at 15 and 40m')
#plt.legend(title='Depth')
plt.savefig('../src/output_images/2002-2024_std 15 and 40')
plt.clf()

# TODO ignorar por el momento
df_filtered_long = df_filtered.reset_index().melt(id_vars='Date', var_name='depth', value_name='temp')
df_new_long = df_new.reset_index().melt(id_vars='Date', var_name='depth', value_name='temp')
df_new_5_long = df_new_5.reset_index().melt(id_vars='Date', var_name='depth', value_name='temp')

# Cambiamos la filtered_long por la new_long
sns.boxplot(x='depth', y='temp', data=df_new_long, showfliers=True, palette=['#d4a19d', '#84cbec'])
plt.title('Temperature distribution whole 2021')
plt.xlabel('Depth')
plt.ylabel('Temperature (ºC)')
plt.savefig('../src/output_images/2021 whole year box')
plt.clf()

sns.boxplot(x='depth', y='temp', data=df_new_long.loc[(df_filtered_long.Date.dt.month>=7) & (df_new_long.Date.dt.month<=9)], showfliers=True, palette=['#d4a19d', '#84cbec'])
plt.title('Temperature distribution JAS 2021')
plt.xlabel('Depth')
plt.ylabel('Temperature (ºC)')
plt.savefig('../src/output_images/2021 JAS box')
plt.clf()

df_filtered_5mean_long = df_filtered_5mean.reset_index().melt(id_vars='Date', var_name='depth', value_name='temp')

sns.boxplot(x='depth', y='temp', data=df_new_5_long, showfliers=True, palette=['#d4a19d', '#84cbec'])
plt.title('Temperature distribution whole series (2002-2024)')
plt.xlabel('Depth')
plt.ylabel('Temperature (ºC)')
plt.savefig('../src/output_images/2002-2024 whole year box')
plt.clf()

df_filtered_5mean_long['Date'] = pd.to_datetime(df_filtered_5mean_long['Date'] + '-2000', format='%m-%d-%Y')

sns.boxplot(x='depth', y='temp', data=df_new_5_long.loc[(df_new_5_long.Date.dt.month>=7) & (df_new_5_long.Date.dt.month<=9)], showfliers=True, palette=['#d4a19d', '#84cbec'])
plt.title('Temperature distribution JAS whole series (2002-2024)')
plt.xlabel('Depth')
plt.ylabel('Temperature (ºC)')
plt.savefig('../src/output_images/2002-2024 JAS box')
plt.clf()
df_thresholds_2021 = df.loc[df['Date'].dt.year==2021].loc[(df['Date'].dt.month >=7) & (df['Date'].dt.month <=9)].groupby(df['Date']).mean()
df_thresholds_5 = df.loc[(df['Date'].dt.year>=2020) & (df['Date'].dt.year<=2024)].loc[(df['Date'].dt.month >=7) & (df['Date'].dt.month <=9)].groupby(df['Date']).mean()

plt.bar(['15', '40'], [df_thresholds_2021.loc[df_thresholds_2021['15'] >=24].count()[0], df_thresholds_2021.loc[df_thresholds_2021['40'] >=24].count()[0] ], color=['#d4a19d', '#84cbec'])
plt.title('Days over 24ºC on 2021')
plt.xlabel('Days')
plt.savefig('../src/output_images/Days over 24ºC on 2021')
plt.clf()
plt.bar(['15', '40'], [df_thresholds_5.loc[df_thresholds_5['15'] >=24].count()[0], df_thresholds_5.loc[df_thresholds_5['40'] >=24].count()[0] ], color=['#d4a19d', '#84cbec'])
plt.title('Days over 24ºC on the whole period (2002-2024)')
plt.xlabel('Days')
plt.savefig('../src/output_images/Days over 24ºC on the whole period (2002-2024)')
plt.clf()

plt.bar(['15', '40'], [df_thresholds_2021.loc[df_thresholds_2021['15'] >=25].count()[0], df_thresholds_2021.loc[df_thresholds_2021['40'] >=25].count()[0] ], color=['#d4a19d', '#84cbec'])
plt.title('Days over 25ºC on 2021')
plt.xlabel('Days')
plt.savefig('../src/output_images/Days over 25ºC on 2021')
plt.clf()
plt.bar(['15', '40'], [df_thresholds_5.loc[df_thresholds_5['15'] >=25].count()[0], df_thresholds_5.loc[df_thresholds_5['40'] >=25].count()[0] ], color=['#d4a19d', '#84cbec'])
plt.title('Days over 25ºC on the whole period (2020-2024)')
plt.xlabel('Days')
plt.savefig('../src/output_images/Days over 25ºC on the whole period (2002-2024)')
plt.clf()

print('hello')




# Box and whiskers plots
'''sns.boxplot(x='Season', y='15', data=df.loc[df['Date'].dt.year == 2022], showfliers=False, palette=['#4682B4', '#98FB98', '#FFD700', '#FF6347'])
plt.xlabel('Season')
plt.ylabel('Temperature ºC')
plt.xticks(ticks=[0,1,2,3], labels=['Winter', 'Spring', 'Summer', 'Autumn'])
plt.title('Temperature per season 2022 at 15m')
plt.savefig('../src/output_images/2022_at15.png')
plt.clf()
sns.boxplot(x='Season', y='20', data=df.loc[df['Date'].dt.year == 2022], showfliers=False, palette=['#4682B4', '#98FB98', '#FFD700', '#FF6347'])
plt.xlabel('Season')
plt.ylabel('Temperature ºC')
plt.xticks(ticks=[0,1,2,3], labels=['Winter', 'Spring', 'Summer', 'Autumn'])
plt.title('Temperature per season 2022 at 20m')
plt.savefig('../src/output_images/2022_at20.png')
plt.clf()

sns.boxplot(x='Season', y='15', data=df.loc[df['Date'].dt.year == 2023], showfliers=False, palette=['#4682B4', '#98FB98', '#FFD700', '#FF6347'])
plt.xlabel('Season')
plt.ylabel('Temperature ºC')
plt.xticks(ticks=[0,1,2,3], labels=['Winter', 'Spring', 'Summer', 'Autumn'])
plt.title('Temperature per season 2023 at 15m')
plt.savefig('../src/output_images/2023_at15.png')
plt.clf()
sns.boxplot(x='Season', y='20', data=df.loc[df['Date'].dt.year == 2023], showfliers=False, palette=['#4682B4', '#98FB98', '#FFD700', '#FF6347'])
plt.xlabel('Season')
plt.ylabel('Temperature ºC')
plt.xticks(ticks=[0,1,2,3], labels=['Winter', 'Spring', 'Summer', 'Autumn'])
plt.title('Temperature per season 2023 at 20m')
plt.savefig('../src/output_images/2023_at20.png')
print('hey')'''