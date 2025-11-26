import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from os import listdir
from os.path import isfile, join
import seaborn as sns
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.ticker as mtick
import zipfile
import imageio.v2 as imageio
from PIL import Image
import cartopy.crs as ccrs
import cartopy.feature as cfeature


EXCEL_PATH = "../src/input_files/activity data/sites_full.xlsx"
SITES_DIR = "../src/input_files/Subidos"
SITES_FILE = "./sites_year_v3.csv"
IMAGE_PATH = "./maps"
LOGO_PATH = "../res/logos/TMEDNET_Black.jpeg"


def ass_points_to_polygons(df, gdf_poly):
    df['geometry'] = df.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf_points = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    gdf_poly = gdf_poly.to_crs(gdf_points.crs)
    joined = gpd.sjoin(gdf_points, gdf_poly, how="left", predicate="within")
    return joined, gdf_points

df = pd.read_csv(SITES_FILE, sep=',')
df['start_year'].loc[df['id'] == 220] = 2024.0
gdf_poly = gpd.read_file("./ecoregions.geojson")


df_data_peryear = pd.DataFrame(range(2002, 2026, 1), columns=['Year'])
joined, gdf_points = ass_points_to_polygons(df, gdf_poly)

df_ecos = pd.DataFrame(joined['ECOREGION'].unique(), columns=['Ecoregion'])
df_data_peryear_ecos = df_data_peryear.merge(df_ecos, how='cross')

df_data_peryear['Count'] = 0

df_data_peryear_ecos['Count'] = 0

err_files = []


df_mpa = pd.read_csv("mapamed.tsv", sep="\t")
gdf_mpa = gpd.read_file("mapamed.gpkg")
gdf_mpa = gdf_mpa.to_crs("EPSG:4326")
gdf_joined = gpd.sjoin(gdf_points, gdf_mpa, how="left", predicate="within")
gdf_site = gdf_joined[gdf_joined['SITE_TYPE_ENG'] == 'Marine Protected Area']

gdf_site_filtered = gdf_site.loc[(gdf_site['MAPAMED_ID'] == gdf_site['PARENT_ID']) & (gdf_site['initialized'] == 1)]

print('u')
def get_data_MPA():
    df = gdf_site.loc[
        (gdf_site['MAPAMED_ID'] == gdf_site['PARENT_ID']) &
        (gdf_site['initialized'] == 1)
        ].copy()

    # 1) Normalitza NAME (opcional però recomanable)
    df['NAME_clean'] = df['NAME'].astype(str).str.strip()

    # 2) Troba la PRIMERA aparició de cada NAME
    first_year = (
        df.groupby('NAME_clean')['start_year']
        .min()
        .reset_index()
        .rename(columns={'start_year': 'first_year'})
    )
    return first_year

mpa_df = get_data_MPA()
def get_MPA(first_year, multi=False):


    # 3) Comptem per any quants NAME tenen primera aparició aquell any
    per_year = (
        first_year.groupby('first_year')['NAME_clean']
        .count()
        .reset_index(name='new_names')
        .sort_values('first_year')
    )

    # 4) Suma acumulada
    per_year['cumulative'] = per_year['new_names'].cumsum()

    print(per_year)

    ax = sns.lineplot(data=per_year, x="first_year", y="cumulative", color='#008080')
    plt.fill_between(per_year['first_year'].values, per_year['cumulative'].values, color='#008080')
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_axisbelow(True)
    plt.xlabel('')
    plt.ylabel('Nº of MPA')
    plt.title('Evolution of MPA with monitoring sites')
    if not multi:
        plt.savefig('insitu_mpa.png')
    else:
        if not np.isnan(multi):
            plt.ylim(YMIN_mpa, YMAX_mpa)
            plt.xlim(XMIN_mpa, XMAX_mpa)
            plt.savefig(f'./sites/insitu_mpa_{int(multi)}.png')

    plt.clf()



df_final = df.loc[df['initialized'] == 1].groupby('start_year').count()['site'].cumsum()
YMAX = df_final.max() + 10
YMIN = 0
XMAX = df_final.index.max()
XMIN = df_final.index.min()


per_year = (
        mpa_df.groupby('first_year')['NAME_clean']
        .count()
        .reset_index(name='new_names')
        .sort_values('first_year')
    )

# 4) Suma acumulada
per_year['cumulative'] = per_year['new_names'].cumsum()
YMAX_mpa = per_year['cumulative'].max() + 10
YMIN_mpa = 0
XMAX_mpa = per_year['first_year'].max()
XMIN_mpa = per_year['first_year'].min()

YMAX_entries = 30000000
YMIN_entries = 0


def compose_excels(sites_dir, excel_path):
    df_excel = pd.read_excel(excel_path, header=0)
    dir_files = [f for f in listdir(sites_dir) if isfile(join(sites_dir, f))]
    cols = ["ID", "Site", "First_year", "Last_year"]
    df_dir = pd.DataFrame(columns=cols)
    for file in dir_files:
        file_split = file.split("_")
        df_dir = pd.concat([df_dir, pd.DataFrame({"ID": [int(file_split[2])], "Site": [file_split[3]], "First_year": [file_split[4][:4]], "Last_year": [file_split[4][7:11]]})])
    return df_dir, df_excel

def merge_excels(df1, df2):
    df_merge = pd.merge(df2, df1,"left", on="ID")
    return df_merge


def paste_logo(baseim, logoim, output):
    # Obrim la imatge base i el logo
    base = Image.open(baseim).convert("RGBA")
    logo = Image.open(logoim).convert("RGBA")
    width = round(892/3)
    heigth = round(280/3)
    logo = logo.resize((width, heigth), Image.LANCZOS)

    margin_heigth = 30
    margin_width = 30
    # Mides
    bw, bh = base.size
    lw, lh = logo.size

    # Triem cantonada (exemples):

    # Cantonada superior dreta
    pos = (bw - lw - margin_width , 0 + margin_heigth)

    # Si el vols a la inferior dreta:
    #pos = (bw - lw - margin, bh - lh - margin)

    # Si el vols a la inferior esquerra:
    # pos = (0, bh - lh)

    # Si el vols a la superior esquerra:
    # pos = (0, 0)

    # Enganxem el logo
    base.paste(logo, pos, logo)

    # Guardem
    base.save(output)

def create_cumsum_sites_plot(df, multi=False):
    df_sites_cumsum = df.loc[df['initialized'] == 1].groupby('start_year').count()['site'].cumsum().rename('total_sites').reset_index()

    ax = sns.lineplot(data=df_sites_cumsum, x="start_year", y="total_sites", color='#008080')
    plt.fill_between(df_sites_cumsum['start_year'].values, df_sites_cumsum['total_sites'].values, color='#008080')
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_axisbelow(True)
    plt.xlabel('')
    plt.ylabel('Nº of sites')
    plt.title(r'Evolution of $\it{in\ situ}$ monitoring sites')
    if not multi:
        plt.savefig('insitu_sites.png')
    else:
        if not np.isnan(multi):
            if int(multi) > 2020:
                print('d')
            plt.ylim(YMIN, YMAX)
            plt.xlim(XMIN, XMAX)
            plt.savefig(f'./sites/insitu_sites_{int(multi)}.png')
    plt.clf()
    df_sites_cumsum.to_excel('sites_cumsum.xlsx')

# TODO order it in ecoregions crossing with the polygons. Should order by year and ecoregion, how?
def read_zip_file(zip_path, ecoregion, eco):
    zip_df = pd.read_csv(zip_path, sep='\t')
    cols = zip_df.columns

    try:
        zip_df['Date'] = pd.to_datetime(zip_df['Date'], dayfirst=True)
        for year in df_data_peryear['Year'].values:
            if not eco:
                df_data_peryear['Count'].loc[
                    (df_data_peryear['Year'] == year)] += np.count_nonzero(
                    ~np.isnan(zip_df.loc[zip_df['Date'].dt.year == year][cols[2:]].values))
            else:
                df_data_peryear_ecos['Count'].loc[(df_data_peryear_ecos['Year'] == year) & (df_data_peryear_ecos['Ecoregion'] == ecoregion)] += np.count_nonzero(~np.isnan(zip_df.loc[zip_df['Date'].dt.year == year][cols[2:]].values))
    except:
        err_files.append(zip_path.split('_')[3])
#TODO DESCARGAR DATABASES DE TMEDNET
def iterate_zipdir(sites_dir, eco):

    dir_files = [f for f in listdir(sites_dir) if isfile(join(sites_dir, f))]
    total_entries = 0
    for file in dir_files:

        ecoregion = joined.loc[joined['id'] == int(file.split('_')[2])]['ECOREGION']
        read_zip_file("../src/input_files/Subidos/" + file, ecoregion.iloc[0], eco)

def create_cumsum_entries_plot(sites_path, multi=False):

    df_entries_cumsum = df_data_peryear.copy()
    if not multi:
        df_entries_cumsum['total_entries'] = df_entries_cumsum['Count'].cumsum()
    else:
        if not np.isnan(multi):
            df_entries_cumsum['total_entries'] = df_entries_cumsum['Count'].loc[df_entries_cumsum['Year'] <= multi].cumsum()
        else:
            return
    ax = sns.lineplot(data=df_entries_cumsum, x="Year", y="total_entries", color='#008080')
    plt.fill_between(df_entries_cumsum['Year'].values, df_entries_cumsum['total_entries'].values, color='#008080')
    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_axisbelow(True)
    plt.xlabel('')
    plt.ylabel('Nº of entries')
    plt.title(r'Evolution of $\it{in\ situ}$ observations')
    formatter = mtick.ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((6, 6))  # Força l'exponent a 10^6
    ax.yaxis.set_major_formatter(formatter)
    if not multi:
        plt.savefig('insitu_entries.png')
        df_entries_cumsum.to_excel('entries_cumsum.xlsx')
    else:
        if not np.isnan(multi):
            plt.ylim(YMIN_entries, YMAX_entries)
            plt.xlim(XMIN, XMAX + 5)
            plt.savefig(f'./sites/insitu_entries_{int(multi)}.png')
    plt.clf()


def create_cumsum_entries_plot_eco(sites_path, multi=False):
    iterate_zipdir(sites_path, True)
    df_entries_cumsum = df_data_peryear_ecos.copy()
    df_entries_cumsum = (
        df_entries_cumsum
        .sort_values(["Ecoregion", "Year"])
        .groupby("Ecoregion", as_index=False)
        .apply(lambda g: g.assign(total_entries=g["Count"].cumsum()))
        .reset_index(drop=True)
    )

    plt.figure(figsize=(10, 6))

    ax = sns.lineplot(
        data=df_entries_cumsum,
        x="Year",
        y="total_entries",
        hue="Ecoregion",
        palette=['#577590', '#43aa8b', '#90be6d', '#f9c74f', '#f8961e',
              '#f3722c', '#f94144']  # opcional, per colors
    )

    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_axisbelow(True)

    plt.xlabel('')
    plt.ylabel('Nº of entries')
    plt.legend(title="Ecoregion")
    plt.title(r'Evolution of $\it{in\ situ}$ observations')
    formatter = mtick.ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((6, 6))  # Força l'exponent a 10^6
    ax.yaxis.set_major_formatter(formatter)
    '''if not multi:
        plt.savefig('insitu_eco.png')
        df_entries_cumsum.to_excel('entries_cumsum.xlsx')
    else:
        if not np.isnan(multi):
            # plt.ylim(YMIN, YMAX)
            plt.xlim(XMIN, XMAX)
            plt.savefig(f'./sites/insitu_eco_{int(multi)}.png')
    
    plt.clf()'''
    plt.clf()

    df_wide = df_entries_cumsum.pivot(index='Year', columns='Ecoregion',
                                      values='total_entries')
    df_wide = df_wide[df_wide.sum().sort_values(ascending=False).index]
    # Fem el stacked line plot
    plt.stackplot(df_wide.index, df_wide.T, labels=df_wide.columns, alpha=0.8,
                                      colors=['#577590', '#43aa8b', '#90be6d', '#f9c74f', '#f8961e',
                                              '#f3722c', '#f94144'])

    ax.yaxis.grid(color='gray', linestyle='dashed')
    ax.set_axisbelow(True)
    plt.legend(loc='upper left', title='Ecoregion')
    plt.xlabel('')
    plt.ylabel('Nº of entries')
    plt.title(r'Evolution of $\it{In\ Situ}$ observations')
    formatter = mtick.ScalarFormatter(useMathText=True)
    formatter.set_powerlimits((6, 6))  # Força l'exponent a 10^6
    ax.yaxis.set_major_formatter(formatter)
    if not multi:
        plt.savefig('insitu_eco.png')
        df_entries_cumsum.to_excel('entries_cumsum.xlsx')
    else:
        if not np.isnan(multi):
            # plt.ylim(YMIN, YMAX)
            plt.xlim(XMIN, XMAX)
            plt.savefig(f'./sites/insitu_eco_{int(multi)}.png')

    plt.clf()


def create_map(lats, lons, year, type):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Fons blau del mar
    ax.set_facecolor('#a6cee3')

    # Afegir costa i línies de terra
    ax.add_feature(cfeature.LAND, facecolor='#f0f0f0')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)

    # Afegir punts
    ax.scatter(lons, lats, color='#E3492B', s=30, transform=ccrs.PlateCarree(), alpha=0.8, zorder=10)

    # Extensió del mapa
    ax.set_extent([-10, 37, 30, 46])  # Ajusta a la teva zona d’estudi
    try:
        # Títol
        if type == 'MME':
            suptitle = r"Evolution of mass mortality events in the Mediterranean"
            title = 'Year: ' + str(int(year)) + ' - #Mass Mortality Records: ' + str(len(lats))
            savefile = f'./maps/map_MME_{int(year)}.png'
        elif type == 'Sites':
            suptitle = r"Evolution of $\it{in\ situ}$ high resolution temperature monitoring sites "
            title = 'Year: ' + str(int(year)) + ' - #Sites: ' + str(len(lats))
            savefile = f'./maps/map_sites_{int(year)}.png'
        ax.set_title(title, fontsize=16)
        fig.suptitle(suptitle, y=0.85)
        # Guardar sense marges blancs
        plt.savefig(savefile, bbox_inches='tight', dpi=300)
        plt.close()
    except:
        print(year)
def yearly_map(df, type):
    lats = []
    lons = []
    df = df.loc[df['start_year'] != 0]
    for year in df.sort_values(by='start_year')['start_year'].unique():
        lats.extend(list(df['latitude'].loc[df['start_year'] == year]))
        lons.extend(list(df['longitude'].loc[df['start_year'] == year]))
        create_map(lats, lons, year, type)


def generate_gif(IMAGE_PATH, type):

    images = []
    '''for filename in filenames:
        images.append(imageio.imread('./maps/'+filename))
    imageio.mimsave('map_sites2.gif', images, duration=0.5)'''
    if type == 'MME':
        savefile = f'./map_MME.gif'
        filenames = [f for f in listdir(IMAGE_PATH) if (isfile(join(IMAGE_PATH, f))) and (f.split('_')[1] == 'MME')]
        frames = [Image.open('./maps/' + img) for img in filenames]
    elif type == 'Sites':
        savefile = f'./map_sites.gif'
        filenames = [f for f in listdir(IMAGE_PATH) if (isfile(join(IMAGE_PATH, f))) and (f.split('_')[1] == 'sites')]
        frames = [Image.open('./maps/' + img) for img in filenames]
    elif type == 'sites_evo':
        savefile = f'./sites_evo.gif'
        filenames = [f for f in listdir(IMAGE_PATH) if (isfile(join(IMAGE_PATH, f))) and (f.split('_')[1] == 'sites')]
        frames = [Image.open('./sites/' + img) for img in filenames]
    elif type == 'mpa':
        savefile = f'./sites_mpa.gif'
        filenames = [f for f in listdir(IMAGE_PATH) if (isfile(join(IMAGE_PATH, f))) and (f.split('_')[1] == 'mpa')]
        frames = [Image.open('./sites/' + img) for img in filenames]
    elif type == 'entries':
        savefile = f'./sites_entries.gif'
        filenames = [f for f in listdir(IMAGE_PATH) if (isfile(join(IMAGE_PATH, f))) and (f.split('_')[1] == 'entries')]
        frames = [Image.open('./sites/' + img) for img in filenames]

    durations = [500] * (len(frames) - 1) + [1500]
    frames[0].save(
        savefile,
        save_all=True,
        append_images=frames[1:],
        duration=durations
    )

def step_by_step_plots():
    years = list(df['start_year'].unique())
    years.sort()
    for year in years:
        create_cumsum_sites_plot(df.loc[df['start_year'] <= year], year)
        create_cumsum_entries_plot(SITES_DIR, year)
        get_MPA(mpa_df.loc[mpa_df['first_year'] <= year], year)
iterate_zipdir(SITES_DIR, False)
#step_by_step_plots()

#create_cumsum_sites_plot(df)
#create_cumsum_entries_plot(SITES_DIR)
#create_cumsum_entries_plot_eco(SITES_DIR)
#generate_gif('./sites', 'mpa')
#generate_gif('./sites', 'sites_evo')
#generate_gif('./sites', 'entries')
#generate_gif(IMAGE_PATH, 'MME')
yearly_map(df.loc[df['initialized'] == 1], 'Sites')
filenames = [f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH, f))]
for file in filenames:
    if file.split('_')[1] == 'sites':
        paste_logo('./maps/'+file, LOGO_PATH, './maps/'+file)
generate_gif(IMAGE_PATH, 'Sites')
'''

step_by_step_plots()
generate_gif("./sites", 'sites_evo')'''


### Creates the maps
'''yearly_map(df.loc[df['initialized'] == 1], 'Sites')
filenames = [f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH, f))]
for file in filenames:
    if file.split('_')[1] == 'sites':
        paste_logo('./maps/'+file, LOGO_PATH, './maps/'+file)
generate_gif(IMAGE_PATH, 'Sites')


df_mme = pd.read_excel("./MME Review dataset.xlsx")
yearly_map(df_mme, 'MME')
filenames = [f for f in listdir(IMAGE_PATH) if isfile(join(IMAGE_PATH, f))]
for file in filenames:
    if file.split('_')[1] == 'MME':
        paste_logo('./maps/'+file, LOGO_PATH, './maps/'+file)
generate_gif(IMAGE_PATH, 'MME')
'''
print('hey')

