import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import data_manager as dm
from scipy.ndimage.filters import uniform_filter1d




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
#plt.show()

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
#plt.show()

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
#plt.show()


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
#plt.show()

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
#plt.show()


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
#plt.show()

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
#plt.show()

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
#plt.show()

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
#plt.show()


#summer
#summer = df[df['Date'].dt.month.isin([7, 8, 9])]
#start of summer
summer = df[df['Date'].dt.month.isin([7, 8, 9])]
summer['day_month'] = summer['Date'].dt.strftime("2000-%m-%d")
#daily_summer = summer.groupby('day_month')[cols].mean()
daily_summer = summer.groupby('Date')[cols].mean().reset_index()
daily_summer['year'] = daily_summer['Date'].dt.year
for col, color in zip(cols, ['#d4a19d', '#84cbec']):
    # Classifica cada dia segons el rang corresponent
    daily_summer[f'{col}_range'] = daily_summer[col].apply(classify_range)

#daily_summer.index = daily_summer.index.astype(str)

# Passem a format llarg (long) per poder fer barres separades per fondària

df_long = pd.melt(
    daily_summer.reset_index(),
    id_vars=['Date', 'year'],
    value_vars=[f'{col}_range' for col in cols],
    var_name='Depth',
    value_name='Range'
)

df_long['Depth'] = df_long['Depth'].str.replace('_range',' m')

# Comptem el número de dies per any, rang i fondària
df_counts = df_long.groupby(['year','Depth','Range']).size().reset_index(name='Count')

# Calculem mitjana i desviació anual per cada rang i fondària
stats = df_counts.groupby(['Depth','Range']).agg(
    Mean=('Count','mean'),
    Std=('Count','std')
).reset_index()

"""# Crear totes les combinacions segons rangs i fondàries
full_index = pd.MultiIndex.from_product(
    [['15 m', '40 m'], ranges],
    names=['Depth', 'Range']
)

# Reindexar i omplir buits amb 0
stats = stats.set_index(['Depth','Range']).reindex(full_index).fillna(0).reset_index()
"""
# Llista dels rangs i fondàries
ranges = stats['Range'].unique()
depths = ['15 m', '40 m']
width = 0.35  # amplada de cada barra
x = np.arange(len(ranges))  # posició de cada rang


'''# --- Barplot amb barres costat a costat ---
plt.figure(figsize=(8, 6))
sns.barplot(
    data=freq,
    x='Range',
    y='Count',
    hue='Depth',
    palette=['#d4a19d', '#84cbec']
)
'''
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
        capsize=5,
    )
plt.xticks(x, ranges)
plt.title('Average number of days per year according to average daily summer temperature (2002-2025) - Medes')
plt.xlabel('Average temperature range (°C)')
plt.ylabel('Days frequency')
plt.legend(title='Depth')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('../src/output_images/days_per_avg.png')

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
bins = np.arange(0, max_val + 3, 3)
#TODO opcio per contar
#daily_range_summer.groupby('15_bin').count()

# Assignem cada valor al seu interval
for col in cols:
    daily_range_summer[f'{col}_bin'] = pd.cut(
        daily_range_summer[col],
        bins=bins,
        right=False,
        labels=[f"{int(b)}–{int(b+3)}" for b in bins[:-1]]
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

x_labels = [f"{int(b)}–{int(b+3)}" for b in bins[:-1]]
plt.xticks(x, x_labels)
plt.title('Average number of days per year by summer range (2002-2025) - Medes')
plt.xlabel('Daily range of variation (°C)')
plt.ylabel('Number of days (annual average)')
plt.legend(title='Depth')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('../src/output_images/range_per_range.png')


print('Plot done')