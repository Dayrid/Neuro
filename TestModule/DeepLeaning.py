import pandas as pd
import numpy as np
import copy
import configparser
class Data_DL:
    def __init__(self, filename):
        self.params = self.cfg()
        self.selected_cols = self.params['selected_cols'].split(',')
        self.df = self.xlsx_read(filename)
        self.single, self.multiple, self.dates = self.get_data(self.df)
        self.x, self.y, self.x_data, self.y_data = self.cube_formation(self.single, self.multiple, self.dates)

    def cfg(self):
        config = configparser.ConfigParser()
        config.read("DL_settings.ini", encoding="utf-8")
        mas = dict(config.items('Settings'))
        return mas

    def xlsx_read(self, filename):
        # Чтение из xlsx формата
        df = pd.read_excel(filename, sheet_name='Уровни', engine='openpyxl')
        df = df[df['Код поста'] == int(self.params['hydropost'])]
        df = df.sort_values('Дата - время')
        df['Дата - время'] = pd.to_datetime(df['Дата - время'])
        df = df.set_index('Дата - время')
        df = df[self.selected_cols]
        df = df.dropna()
        pd.options.display.max_columns = None
        pd.options.display.max_rows = None
        return df
    def get_data(self, df):
        single = df[self.selected_cols].values.tolist()
        multiple = df.values.tolist()
        dates = df.index.astype('str').values.tolist()
        return single, multiple, dates
    def cube_formation(self, single, multiple, dates):
        dates_y = copy.deepcopy(dates)
        single, multiple, dates, dates_y = single[::-1], multiple[::-1], dates[::-1], dates_y[::-1]
        ind = dates.index(self.params['end_date'])
        multiple, dates = multiple[:ind+1], dates[:ind+1]
        x = copy.deepcopy(self.data_split(multiple, int(self.params['fh'])))
        date_cube = copy.deepcopy(self.data_split(dates, int(self.params['fh'])))
        y = single[int(self.params['fh']):len(x)+int(self.params['fh'])]
        x_data, y_data = copy.deepcopy(x), copy.deepcopy(y)
        y_data = [[i] for i in y]
        dates_y = dates_y[int(self.params['fh']):len(dates)+int(self.params['fh'])]
        for i in range(len(x)):
            y_data[i].insert(0, dates_y[i])
        for i in range(len(x)):
            for j in range(len(x[i])):
                x_data[i][j].insert(0, date_cube[i][j])
        # for i in range(len(x_data)):
        #     print(x_data[i], y_data[i])
        return x, y, x_data, y_data
    def data_split(self, data: list, n: int):
        newdata = []
        for i in range(len(data) - n + 1):
            newdata.append(copy.deepcopy(data[i:i + n]))
        return newdata
obj = Data_DL('Urovni2_1_1_new.xlsx')