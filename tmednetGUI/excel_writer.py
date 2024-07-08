import numpy as np
import pandas as pd
import time
from pandas import ExcelWriter
import marineHeatWaves as mhw
import datetime


class ExcelReport:

    def __init__(self, filein):
        self.dfexcel = []
        self.dfmonthly = []
        self.dfseasonal = []
        self.mhwdf = []
        self.filein = filein

    # Converts the data from the historic file to a DataFrame and selects the needed data to create the Excel
    def excel_writer(self):
        start = time.time()
        # Reads the historic file and converts it to a DataFrame. Loads all the DataFrames to make the calculations
        self.read_and_setup()
        # Sorts the final DataFrames that will compose the sheets of the Excel file
        self.dfexcel['depth(m)'] = self.dfexcel['depth(m)'].astype(int)
        self.dfmonthly['depth(m)'] = self.dfmonthly['depth(m)'].astype(int)
        self.dfexcel = self.dfexcel.sort_values(by=['date', 'depth(m)'])
        self.dfmonthly = self.dfmonthly.sort_values(by=['year', 'month', 'depth(m)'])
        self.dfseasonal['depth(m)'] = self.dfseasonal['depth(m)'].astype(int)
        self.dfseasonal = self.dfseasonal.sort_values(by=['year', 'depth(m)'])
        self.dfexcel['year'] = pd.DatetimeIndex(self.dfexcel['date']).year
        self.dfexcel['month'] = pd.DatetimeIndex(self.dfexcel['date']).month
        self.dfexcel['date'] = self.dfexcel['date'].dt.date
        dfmaxes = self.dfexcel.loc[self.dfexcel.groupby(['year'])['max'].idxmax()][['year', 'date', 'max']]
        dfmaxes.sort_values('max', ascending=False, inplace=True)
        dfmaxesdepth = self.dfexcel.loc[self.dfexcel.groupby(['year', 'depth(m)'])['max'].idxmax().dropna()][
            ['year', 'depth(m)', 'date', 'max']]
        dfmaxesdepth.sort_values(['depth(m)', 'max'], ascending=False, inplace=True)
        dfmaxes_month = self.dfexcel.loc[self.dfexcel.groupby(['year', 'month'])['max'].idxmax()][['year', 'month', 'date', 'max']]
        dfmaxes_month.sort_values('max', ascending=False, inplace=True)
        dfmaxesdepth_month = self.dfexcel.loc[self.dfexcel.groupby(['year', 'month', 'depth(m)'])['max'].idxmax().dropna()][
            ['year', 'month', 'depth(m)', 'date', 'max']]
        dfmaxesdepth_month.sort_values(['depth(m)', 'max'], ascending=False, inplace=True)
        # Write the Excel file with the given DataFrames as sheets
        filein_split = self.filein.split('_')
        fileout_name = filein_split[3] + '_Stat_Report_' + filein_split[4] + '_' + filein_split[5][:-4]
        writer = ExcelWriter('../src/output_files/' + fileout_name + '.xlsx')
        self.dfexcel.to_excel(writer, 'Daily', index=False)
        self.dfmonthly.to_excel(writer, 'Monthly', index=False)
        self.dfseasonal.to_excel(writer, 'Seasonal', index=False)
        dfmaxes.to_excel(writer, 'Maxes', index=False)
        dfmaxesdepth.to_excel(writer, 'Maxes depth', index=False)
        dfmaxes_month.to_excel(writer, 'Maxes month', index=False)
        dfmaxesdepth_month.to_excel(writer, 'Maxes depth month', index=False)
        write_mhw = self.__check_year_difference()
        if write_mhw:
            mhw_sheet = self.create_mhw()
            mhw_sheet.to_excel(writer, 'MHW', index=False)
            mhw_sheet['year'] = pd.DatetimeIndex(mhw_sheet['Date']).year
            dfmaxesmhw = mhw_sheet.loc[mhw_sheet.groupby(['year', 'Depth (m)'])['Max Intensity (ºC)'].idxmax().dropna()]
            dfmaxesmhw.sort_values(['Date'], ascending=True, inplace=True)
            dfmaxesmhw.to_excel(writer, 'MHW_MAX I', index=False)

        writer.save()
        end = time.time()
        print(end - start)

    def read_and_setup(self):
        df = pd.read_csv(self.filein, sep='\t')
        self.mhwdf = df.copy()
        depths = df.columns.tolist()
        del depths[0]
        del depths[0]
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df['year'] = df['Date'].dt.year
        df['month'] = df['Date'].dt.month
        dfinter = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])

        self.dfexcel = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])
        self.dfmonthly = pd.DataFrame(
            columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                     'Ndays>=26'])
        dfintermonth = pd.DataFrame(
            columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                     'Ndays>=26'])
        self.dfseasonal = pd.DataFrame(
            columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                     'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])
        dfinterseason = pd.DataFrame(
            columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                     'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])
        # Iterates for each depth (which is a column on the historic DataFrame) and appends to the final excel DataFrame
        for depth in depths:
            # Setting up
            dfinter = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])
            dfintermonth = pd.DataFrame(
                columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                         'Ndays>=26'])
            dfinterseason = pd.DataFrame(
                columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                         'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])
            temp = df.groupby('Date')[str(depth)]
            tempmonth = df.groupby(['year', 'month'])[str(depth)]
            #TODO consider include June (month 6)
            tempseason = df.loc[(df['month'] >= 7) & (df['month'] <= 9)].groupby(['year'])[str(depth)]
            last_year = df['year'][len(df) - 1]
            # temphist = df.loc[(df['month'] >= 7) & (df['month'] <= 9) & (df['year'] < last_year)][str(depth)]
            depto = np.repeat(depth, len(temp)).tolist()
            deptomonth = np.repeat(depth, len(tempmonth.count())).tolist()
            deptoseason = np.repeat(depth, len(tempseason)).tolist()

            # Daily Calculations
            dfinter['date'] = temp.count().index.tolist()
            dfinter['N'] = temp.count().values
            dfinter['mean'] = temp.mean().values.round(3)
            dfinter['std'] = temp.std().values.round(3)
            dfinter['max'] = temp.max().values.round(3)
            dfinter['min'] = temp.min().values.round(3)
            dfinter['depth(m)'] = depto

            # Monthly Calculations
            dfintermonth['year'] = tempmonth.count().index.get_level_values(0).to_list()
            dfintermonth['month'] = tempmonth.count().index.get_level_values(1).to_list()
            dfintermonth['depth(m)'] = deptomonth
            dfintermonth['N'] = tempmonth.count().values
            dfintermonth['mean'] = tempmonth.mean().values.round(3)
            dfintermonth['std'] = tempmonth.std().values.round(3)
            dfintermonth['min'] = tempmonth.min().values.round(3)
            dfintermonth['max'] = tempmonth.max().values.round(3)
            dfintermonth['Ndays>=24'] = np.round(tempmonth.apply(lambda x: x[x >= 24].count()).values / 24)
            dfintermonth['Ndays>=25'] = np.round(tempmonth.apply(lambda x: x[x >= 25].count()).values / 24)
            dfintermonth['Ndays>=26'] = np.round(tempmonth.apply(lambda x: x[x >= 26].count()).values / 24)

            # Seasonal Calculations
            dfinterseason['year'] = tempseason.count().index.to_list()
            dfinterseason['season'] = np.repeat(3, len(tempseason)).tolist()
            dfinterseason['depth(m)'] = deptoseason
            dfinterseason['N'] = tempseason.count().values
            dfinterseason['mean'] = tempseason.mean().values.round(3)
            # dfinterseason['hist_mean'] = np.round(temphist.mean(), 3)
            dfinterseason['std'] = tempseason.std().values.round(3)
            # dfinterseason['hist_std'] = np.round(temphist.std(), 3)
            dfinterseason['min'] = tempseason.min().values.round(3)
            # dfinterseason['hist_min'] = np.round(temphist.min(), 3)
            dfinterseason['max'] = tempseason.max().values.round(3)
            # dfinterseason['hist_max'] = np.round(temphist.max(), 3)
            dfinterseason['Ndays>=23'] = np.round(tempseason.apply(lambda x: x[x >= 23].count()).values / 24)
            dfinterseason['Ndays>=24'] = np.round(tempseason.apply(lambda x: x[x >= 24].count()).values / 24)
            dfinterseason['Ndays>=25'] = np.round(tempseason.apply(lambda x: x[x >= 25].count()).values / 24)
            dfinterseason['Ndays>=26'] = np.round(tempseason.apply(lambda x: x[x >= 26].count()).values / 24)
            dfinterseason['Ndays>=27'] = np.round(tempseason.apply(lambda x: x[x >= 27].count()).values / 24)
            dfinterseason['Ndays>=28'] = np.round(tempseason.apply(lambda x: x[x >= 28].count()).values / 24)

            self.dfexcel = self.dfexcel.append(dfinter, ignore_index=True)
            self.dfmonthly = self.dfmonthly.append(dfintermonth, ignore_index=True)
            self.dfseasonal = self.dfseasonal.append(dfinterseason, ignore_index=True)

    # This method uses the mhw library to return the mhw of a given historic file.
    def create_mhw(self):
        del self.mhwdf['Time']
        self.mhwdf['Date'] = pd.to_datetime(self.mhwdf['Date'], format='%d/%m/%Y')
        nufile = self.mhwdf.groupby('Date').mean()
        dates = [x.date() for x in nufile.index]
        t = [x.toordinal() for x in dates]
        t = np.array(t)
        depths = nufile.columns
        sst5 = nufile[depths[0]].values
        mhws, clim = mhw.detect(t, sst5)
        diff = pd.DataFrame(
            {'Date': mhws['date_start'], 'Depth (m)': depths[0], 'Duration (Days)': mhws['duration'],
             'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
             'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']],
             'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']],
             'Mean Temperature (ºC)': [round(sst5[item[0]:item[0]+item[1]].mean(), 2) for item in zip(mhws['index_start'], mhws['duration'])]})
        for depth in depths:
            if depth == depths[0]:
                pass
            else:
                sst = nufile[depth].values
                mhws, clim = mhw.detect(t, sst)
                dfi = pd.DataFrame(
                    {'Date': mhws['date_start'], 'Depth (m)': depth, 'Duration (Days)': mhws['duration'],
                     'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
                     'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']],
                     'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']],
                     'Mean Temperature (ºC)': [round(sst[item[0]:item[0]+item[1]].mean(), 2) for item in zip(mhws['index_start'], mhws['duration'])]})
                diff = diff.append(dfi, ignore_index=True)

        return diff

    def __check_year_difference(self):
        lastyear = self.dfexcel['date'].iloc[-1].year
        firstyear = self.dfexcel['date'].iloc[0].year
        lastmonth = self.dfexcel['date'].iloc[-1].month
        firstmonth = self.dfexcel['date'].iloc[0].month
        if lastmonth < firstmonth:
            years = lastyear - firstyear
        else:
            years = lastyear - firstyear - 1
        if years >= 10:
            write_mhw = True
        else:
            write_mhw = False

        return write_mhw
