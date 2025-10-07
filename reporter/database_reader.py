import numpy as np
import pandas as pd
from zipfile import ZipFile
from os import listdir
from os.path import isfile, join
import tmednetGUI.marineHeatWaves as mhwcalc
import tmednetGUI.mhw_calculations as mhwc


class TMEDNetDatabase:

    def __init__(self, dir="../src/input_files/Subidos/"):
        self.dir = dir
        self.df_dicts = self.__create_df_dict()
        self.df_dicts_mhw = {}

    def get_df_dicts(self):
        return self.df_dicts

    @staticmethod
    def __calculate_percentile(df, cols, percentile_up, percentile_down):
        # Calculate the threshold according to the percentile
        thresholds_up = df[cols].quantile(percentile_up)
        thresholds_down = df[cols].quantile(percentile_down)

        # Returns the new df according to the threshold and type
        df_clean = df.copy()
        for col in cols:
            df_clean.loc[df_clean[col] > thresholds_up[col], col] = float("nan")
            df_clean.loc[df_clean[col] < thresholds_down[col], col] = float("nan")

        return df_clean
    @staticmethod
    def __temp_series_setter(df, temp_cols, filename):
        # Searches and stores the max and min indexes
        max_row_idx = df[temp_cols].idxmax().max()
        min_row_idx = df[temp_cols].idxmin().min()

        # Searches and stores the max and min dates
        max_date = df.loc[max_row_idx, 'Date']
        min_date = df.loc[min_row_idx, 'Date']

        # Sets the Series containing the data for the given file
        max_series = pd.DataFrame([{'Filename': filename, 'MaxDate': max_date, 'Max': float(df[temp_cols].max().max())}])
        min_series = pd.DataFrame([{'Filename': filename, 'MinDate': min_date, 'Min': float(df[temp_cols].min().min())}])

        return max_series, min_series

    @staticmethod
    def __top_ten_creator(df, temp_cols, top_ten_max_temps, top_ten_min_temps, max_series, min_series):
        # Stores into the dfs only if they are inside the TOP10
        if len(top_ten_max_temps) < 10:
            top_ten_max_temps = pd.concat([top_ten_max_temps, max_series], ignore_index=True)
            top_ten_min_temps = pd.concat([top_ten_min_temps, min_series], ignore_index=True)
        elif float(df[temp_cols].max().max()) > top_ten_max_temps['Max'].min():
            top_ten_max_temps.drop(top_ten_max_temps['Max'].idxmin(), inplace=True)
            top_ten_max_temps = pd.concat([top_ten_max_temps, max_series], ignore_index=True)
        elif float(df[temp_cols].min().min()) < top_ten_min_temps['Min'].max():
            top_ten_min_temps.drop(top_ten_min_temps['Min'].idxmax(), inplace=True)
            top_ten_min_temps = pd.concat([top_ten_min_temps, min_series], ignore_index=True)

        return top_ten_max_temps, top_ten_min_temps

    def __create_df_dict(self):
        mega_dir_list = [f for f in listdir(self.dir) if isfile(join(self.dir, f))]

        # Sets a dict to store all the DataBases insides the big ZIP file
        dico_dfs_txt = {}

        # Creates said dict by scraping the info inside the ZIP file
        for zip_filename in mega_dir_list:
            zip_file = ZipFile(self.dir + zip_filename)
            for file in zip_file.namelist():
                if file.endswith(".txt"):
                    temp_df = pd.read_csv(zip_file.open(file), sep='\t')
                    temp_df = self.__calculate_percentile(temp_df, temp_df.columns[2:], 0.99, 0.01)
                    # Converts Date column to Datetime format
                    temp_df['Date'] = pd.to_datetime(temp_df['Date'], format='%d/%m/%Y')
                    dico_dfs_txt[file] = temp_df
        return dico_dfs_txt

    def create_top_tens(self, year):
        dico_temps = {}
        top_ten_max_temps = pd.DataFrame(columns=['Filename', 'MaxDate', 'Max'])
        top_ten_min_temps = pd.DataFrame(columns=['Filename', 'MinDate', 'Min'])
        # Sets the df for a given year, not historic
        top_ten_max_temps_given_year = pd.DataFrame(columns=['Filename', 'MaxDate', 'Max'])
        top_ten_min_temps_given_year = pd.DataFrame(columns=['Filename', 'MinDate', 'Min'])
        year = year

        # Search in each df for the highest and lowest temperature
        for filename, df in self.df_dicts.items():
            dico_temps[filename] = {'max': float(df[df.columns[2:]].max().max()), 'min': float(df[df.columns[2:]].min().min())}

            # Sets the df of the given year
            df_year = df.loc[df['Date'].dt.year == year]

            temp_cols = df.columns[2:]

            # Series for the historic values
            max_series, min_series = self.__temp_series_setter(df, temp_cols, filename)

            # Gets the TOP10 for the historic values
            top_ten_max_temps, top_ten_min_temps = self.__top_ten_creator(df, temp_cols, top_ten_max_temps, top_ten_min_temps, max_series, min_series)

            if not df_year.empty:
                # Series for the given year values
                max_series_year, min_series_year = self.__temp_series_setter(df_year, temp_cols, filename)

                # Gets the TOP10 for the given year values
                top_ten_max_temps_given_year, top_ten_min_temps_given_year = self.__top_ten_creator(df, temp_cols, top_ten_max_temps_given_year,
                                                                                            top_ten_min_temps_given_year,
                                                                                            max_series_year, min_series_year)

        top_ten_max_temps_given_year = top_ten_max_temps_given_year.sort_values(by='Max', ascending=False)
        top_ten_min_temps_given_year = top_ten_min_temps_given_year.sort_values(by='Min', ascending=True)
        top_ten_max_temps = top_ten_max_temps.sort_values(by='Max', ascending=False)
        top_ten_min_temps = top_ten_min_temps.sort_values(by='Min', ascending=True)

        return top_ten_max_temps, top_ten_min_temps, top_ten_min_temps_given_year, top_ten_max_temps_given_year

    def create_dict_with_mhw_able_dfs(self):
        # Stores in a new dict only the dfs with more than 10 years of data, which are the ones that can give MHW data
        for filename, df in self.df_dicts.items():
            if df['Date'][len(df) - 1].year - df['Date'][0].year >= 10:
                self.df_dicts_mhw[filename] = df


    def mhw_at_5(self):
        # Stores in a dict all the data of mhws.
        self.create_dict_with_mhw_able_dfs()
        self.dict_mhw = {}
        for filename, df in self.df_dicts_mhw.items():
            df_mhw = mhwc.create_df_with_mhw(df)
            self.dict_mhw[filename] = df_mhw


    #TODO read reports to get ideas on new metrics