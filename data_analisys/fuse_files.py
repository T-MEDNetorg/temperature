import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join
import geopandas as gpd
import compose_excels as ce
import main_data_analysis as mda
from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
file_paths = [BASE_DIR / "OdM_old", BASE_DIR / "OdM"]
LOGO_TMEDNET_PATH = "../res/logos/TMEDNET_Black.jpeg"
LOGO_ODM_PATH = "../res/logos/odm-cast-azul.png"

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

def create_joined_odmfile(file_path):
    filenames = [f for f in listdir(file_path) if isfile(join(file_path, f))]

    cols = ['Project', 'Date of observation', 'Latitude', 'Longitude']

    df_results = pd.read_csv(file_path / filenames[0])[cols]
    for file in filenames[1:]:
        print(file)
        try:
            df = pd.read_csv(file_path / file)

            df_results = pd.concat([df_results, df[cols]])
        except:
            cols2 = ["Project", "Date de l observation", "Lat", "Long"]
            df = pd.read_excel(file_path / file)
            try:
                df = df.rename(columns={"Date de l observation": "Date of observation", "Lat": "Latitude", "Long": "Longitude"})
            except:
                print("not")
            df_results = pd.concat([df_results, df[cols]])
            print('error')
    return df_results


### This bunch creates MPA excel
def create_mpa_df(df_results, cols = ['Project', 'Latitude', 'Longitude', 'NAME']):


    df_mpa = pd.read_csv("mapamed.tsv", sep="\t")
    gdf_mpa = gpd.read_file("mapamed.gpkg")
    gdf_mpa = gdf_mpa.to_crs("EPSG:4326")
    if type(df_results) is dict:
        projects = df_results.keys()
    else:
        projects = df_results['Project'].unique()
    first = True
    for proj in projects:
        if type(df_results) is dict:
            df = df_results[proj]
        else:
            df = df_results.loc[df_results['Project'] == proj]

        joined, gdf_points = ce.ass_points_to_polygons(df)
        gdf_joined = gpd.sjoin(gdf_points, gdf_mpa, how="left", predicate="within")
        gdf_site = gdf_joined[gdf_joined['SITE_TYPE_ENG'] == 'Marine Protected Area']
        gdf_site = gdf_site.loc[(gdf_site['MAPAMED_ID'] == gdf_site['PARENT_ID'])]
        gdf_site['NAME'] = gdf_site['NAME'].astype(str).str.strip()
        if first:
            df_MPAS = gdf_site[cols]
            first = False
        else:
            df_MPAS = pd.concat([df_MPAS, gdf_site[cols]])

    return df_MPAS

def get_tmed_dict(df, year):
    df_dict = {}
    for proj in df['Project'].unique():
        df_dict['{0}'.format(proj)] = df.loc[df['Project'] == proj]  # removed drop duplicates
    df_dict['All'] = df  # removed drop duplicates

    for key in df_dict.keys():
        lats = df_dict[key]['Latitude']
        lons = df_dict[key]['Longitude']
        mda.create_map(lats, lons, key, year)

    return df_dict


def odm_pipe():
    for file_path in file_paths:
        df_results = create_joined_odmfile(file_path)
        # Mask for cantabric values
        mask = (
            (df_results['Latitude'] >=  38.584924) &
            (df_results['Longitude'] <= -0.484246)
        )
        df_results = df_results.loc[~mask]

        mda.create_map(df_results['Latitude'], df_results['Longitude'], str(file_path).split('\\')[-1])

        df_results.groupby(by='Project')['Latitude'].count().to_excel(f'./results/OdM_Counts_{str(file_path).split('\\')[-1]}.xlsx')

        df_MPAS = create_mpa_df(df_results)
        # df_MPAS = df_MPAS.drop_duplicates()
        df_MPAS.groupby(by=['NAME', 'Project']).count()['Latitude'].to_excel(f'./results/MPAODM_{str(file_path).split('\\')[-1]}.xlsx')

    paste_logo('./maps/map_OdM_2024-2025.png', LOGO_ODM_PATH, './maps/map_OdM_2024-2025_logo.png')
    paste_logo('./maps/map_OdM_pre2024.png', LOGO_ODM_PATH, './maps/map_OdM_pre2024_logo.png')



def tmednet_pipe():
    cols = ['Project', 'Latitude', 'Longitude']
    df_post24 = pd.read_excel('Data T-MEDNet 2025_12_15_V2.xlsx', sheet_name='T-MEDNet post 2024')
    df_post24 = df_post24[cols]
    df_pre24 = pd.read_excel('Data T-MEDNet 2025_12_15_V2.xlsx', sheet_name='T-MEDNet pre 2024')
    df_pre24 = df_pre24[cols]

    df_dict_pre = get_tmed_dict(df_pre24, "pre")
    df_pre24.groupby(by='Project')['Latitude'].count().to_excel(
        f'./results/TMEDNET_Counts_pre.xlsx')
    df_dict_post = get_tmed_dict(df_post24, "post")
    df_post24.groupby(by='Project')['Latitude'].count().to_excel(
        f'./results/TMEDNET_Counts_post.xlsx')

    df_MPAS = create_mpa_df(df_dict_pre)
    df_MPAS.groupby(by=['NAME', 'Project']).count()['Latitude'].to_excel(
        f'./results/MPATMEDNET_pre.xlsx')

    df_MPAS = create_mpa_df(df_dict_post)
    df_MPAS.groupby(by=['NAME', 'Project']).count()['Latitude'].to_excel(
        f'./results/MPATMEDNET_post.xlsx')


def temp_pipe():
    df = pd.read_csv("sites_year_v5.csv")

    cols = ['latitude', 'longitude', 'start_year', 'NAME']
    df_mpa = pd.read_csv("mapamed.tsv", sep="\t")
    gdf_mpa = gpd.read_file("mapamed.gpkg")
    gdf_mpa = gdf_mpa.to_crs("EPSG:4326")
    joined, gdf_points = ce.ass_points_to_polygons(df.loc[df['initialized'] == 1])
    gdf_joined = gpd.sjoin(gdf_points, gdf_mpa, how="left", predicate="within")
    gdf_site = gdf_joined[gdf_joined['SITE_TYPE_ENG'] == 'Marine Protected Area']
    gdf_site = gdf_site.loc[(gdf_site['MAPAMED_ID'] == gdf_site['PARENT_ID'])]
    gdf_site['NAME'] = gdf_site['NAME'].astype(str).str.strip()
    df_MPAS = gdf_site[cols]
    df_MPAS.groupby(by=['start_year', 'NAME']).count()['latitude'].to_excel(
        f'./results/MPATemp.xlsx')

    print('finished')

def maps_pipes():
    df = pd.read_csv("sites_year_v6.csv")
    df_post24 = pd.read_excel('Data T-MEDNet 2025_12_15_V2.xlsx', sheet_name='T-MEDNet post 2024')
    df_preclean = df_post24[['Latitude', 'Longitude']].loc[df_post24['Project'] != 'MME']
    df_clean = df.loc[(df['initialized'] == 1) & ((df['start_year'].isna()) | (df['start_year'] > 2023))][['latitude', 'longitude']].rename(columns={'latitude': 'Latitude', 'longitude':'Longitude'})
    dfinitive = pd.concat([df_preclean, df_clean], ignore_index=True)
    ls = [37.0150, -8.9154]
    dfinitive = pd.concat(
        [dfinitive, pd.DataFrame([ls], columns=dfinitive.columns)],
        ignore_index=True
    )
    mda.create_map(dfinitive['Latitude'], dfinitive['Longitude'], 'All', "post")
    paste_logo('./maps/map_All_post.png', LOGO_TMEDNET_PATH, './maps/map_All_post_logo.png')
    print('ha')

def main():
    #odm_pipe()
    #tmednet_pipe()
    #temp_pipe()
    maps_pipes()
    """df_post24 = pd.read_excel('Data T-MEDNet 2025_12_15_V2.xlsx', sheet_name='T-MEDNet post 2024')
    df_preclean = df_post24[['Latitude', 'Longitude']].loc[df_post24['Project'] == 'MME']
    mda.create_map(df_preclean['Latitude'], df_preclean['Longitude'], 'MME', "post")
    paste_logo('./maps/map_MME_post.png', LOGO_TMEDNET_PATH, './maps/map_MME_post_logo.png')"""





    print('hey')

if __name__ == "__main__":
    main()