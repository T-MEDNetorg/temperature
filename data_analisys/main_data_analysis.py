import compose_excels as ce
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


def create_map(lats, lons, type, year="pre"):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # Fons blau del mar
    ax.set_facecolor('#a6cee3')

    # Afegir costa i línies de terra
    ax.add_feature(cfeature.LAND, facecolor='#f0f0f0')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4)

    # Afegir punts color='#0267b0'
    ax.scatter(lons, lats, color='#0267b0', s=15, transform=ccrs.PlateCarree(), alpha=0.8, zorder=10)

    # Extensió del mapa
    ax.set_extent([-10, 37, 30, 46])  # Ajusta a la teva zona d’estudi
    if year == "pre":
        supti = "Historic series prior 2024"
    else:
        supti = "Years 2024-2025"
    # Títol
    if type == 'MME':
        suptitle = r"Mass mortality events in the Mediterranean"
        title = f'{supti} - #Mass Mortality Records: ' + str(len(lats))
        savefile = f'./maps/map_MME_{year}.png'
    elif type == 'Monitoring Mortality':
        suptitle = r"Monitoring Mortality sites in the Mediterranean"
        title = f'{supti} - #Monitoring Mortality Records: ' + str(len(lats))
        savefile = f'./maps/map_MMort_{year}.png'
    elif type == 'Fish Visual Census':
        suptitle = r"Fish Visual Census sites in the Mediterranean"
        title = f'{supti} - #Fish Visual Census Records: ' + str(len(lats))
        savefile = f'./maps/map_FVC_{year}.png'
    elif type == 'POFA':
        suptitle = r"Posidonia sites in the Mediterranean"
        title = f'{supti} - #Posidonia Records: ' + str(len(lats))
        savefile = f'./maps/map_POFA_{year}.png'
    elif type == 'URCH':
        suptitle = f"Urchins sites in the Mediterranean"
        title = f'{supti} - #Urchins Records: ' + str(len(lats))
        savefile = f'./maps/map_URCH_{year}.png'
    elif type == 'All':
        suptitle = f"Monitoring sites in the Mediterranean"
        title = f'{supti} - Number of ecological surveys: ' + str(len(lats))
        savefile = f'./maps/map_All_{year}.png'
    elif type == 'OdM_old':
        suptitle = r"OdM Observations in the Mediterranean"
        title = 'Historic series prior 2024 - #Records: ' + str(len(lats))
        savefile = './maps/map_OdM_pre2024.png'
    elif type == 'OdM':
        suptitle = r"OdM Observations in the Mediterranean"
        title = 'Years 2024-2025 - #Records: ' + str(len(lats))
        savefile = './maps/map_OdM_2024-2025.png'

    ax.set_title(title, fontsize=16)
    fig.suptitle(suptitle, y=0.85)
    # Guardar sense marges blancs
    plt.savefig(savefile, bbox_inches='tight', dpi=300)
    plt.close()



#ce.step_by_step_plots()
#ce.generate_gif('./sites', 'mpa')
#ce.generate_gif('./sites', 'sites_evo')
#ce.generate_gif('./sites', 'entries')

#ce.all_plots()

'''
df = pd.read_excel("./Data T-MEDNet 2025_12_15.xlsx", sheet_name='Coord')
cols = df.columns[:-1]
df = df[cols]
df_dict = {}
for proj in df['Project'].unique():
    df_dict['{0}'.format(proj)] = df.loc[df['Project'] == proj] # removed drop duplicates
df_dict['All'] = df # removed drop duplicates


for key in df_dict.keys():
    lats = df_dict[key]['Latitude']
    lons = df_dict[key]['Longitude']
    create_map(lats, lons, key)


cols = ['Project', 'Latitude', 'Longitude', 'NAME']
'''

'''df_mpa = pd.read_csv("mapamed.tsv", sep="\t")
gdf_mpa = gpd.read_file("mapamed.gpkg")
gdf_mpa = gdf_mpa.to_crs("EPSG:4326")
for key in df_dict.keys():
    joined, gdf_points = ce.ass_points_to_polygons(df_dict[key])
    gdf_joined = gpd.sjoin(gdf_points, gdf_mpa, how="left", predicate="within")
    gdf_site = gdf_joined[gdf_joined['SITE_TYPE_ENG'] == 'Marine Protected Area']
    gdf_site = gdf_site.loc[(gdf_site['MAPAMED_ID'] == gdf_site['PARENT_ID'])]
    gdf_site['NAME'] = gdf_site['NAME'].astype(str).str.strip()
    if key == 'MME':
        df_MPAS = gdf_site[cols]
    else:
        df_MPAS = pd.concat([df_MPAS, gdf_site[cols]])

df_MPAS = df_MPAS.drop_duplicates()

df_MPAS.to_excel('output_MPAS.xlsx')'''

print('hey')
