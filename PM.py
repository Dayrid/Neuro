import csv
import configparser
import pandas as pd
import datetime
import copy
from RecoverDataFrame import *
from RecoverDataFrame import naive_bayes


class Data:

    def cfg(self):
        config = configparser.ConfigParser()
        config.read("settings.ini", encoding="utf-8")
        mas = dict(config.items('Settings'))
        return mas

    '''Конструктор класса Data
    Здесь идет формирование готовых для использования данных
    '''
    def __init__(self, filename: str):
        self.params = self.cfg()
        self.df = self.xlsx_read(filename)
        self.restored_df = copy.deepcopy(self.df)
        self.selected_cols = self.params['selectedcols'].split(',')
        # Тут
        self.multiple_restored, self.single, self.dates, self.multiple_restored_dates, self.single_dates = self.get_data_new(
            self.df)
        self.x, self.y, self.x_data, self.y_data = self.cube_formation(self.multiple_restored, self.single,
                                                                       self.multiple_restored_dates, self.single_dates)
        self.x_data, self.y_data, self.x, self.y = self.clean_new(self.x_data, self.y_data, self.x, self.y)
        self.a_min, self.a_max, self.x = self.normal(self.x)
        self.y = self.normal_y(self.y, self.a_min, self.a_max)

    '''Функция нормализации массива x в классе Data
    Вход:
    x: array (значения ~ a_min-a_max)
    Выход:
    x: array (значения ~ 0-1)
    '''
    def normal(self, x):
        a_min = [100000] * len(x[0][0])
        a_max = [-100000] * len(x[0][0])
        for i in range(len(x)):
            for j in range(len(x[i])):
                for k in range(len(x[i][j])):
                    a_min[k] = min(a_min[k], x[i][j][k])
                    a_max[k] = max(a_max[k], x[i][j][k])

        for i in range(len(x)):
            for j in range(len(x[i])):
                for k in range(len(x[i][j])):
                    x[i][j][k] = (x[i][j][k] - a_min[k]) / (a_max[k] - a_min[k])

        return a_min, a_max, x

    '''Функция нормализации массива y в классе Data
    Вход:
    y: array (значения ~ a_min-a_max)
    Выход:
    y: array (значения ~ 0-1)
    '''
    def normal_y(self, y, a_min, a_max):
        for i in range(len(y)):
            for j in range(len(y[i])):
                y[i][j] = (y[i][j] - a_min[0]) / (a_max[0] - a_min[0])
        return y

    '''Функция денормализации массива x в классе Data
    Вход:
    x: array (значения ~ 0-1)
    Выход:
    x: array (значения ~ a_min-a_max)
    '''
    def denormal(self, x):
        for i in range(len(x)):
            for j in range(len(x[i])):
                for k in range(len(x[i][j])):
                    x[i][j][k] = (x[i][j][k]) * (self.a_max[k] - self.a_min[k]) + self.a_min[k]
        return x

    '''Функция денормализации массива y в классе Data
    Вход:
    y: array (значения ~ 0-1)
    Выход:
    y: array (значения ~ a_min-a_max)
    '''
    def denormal_y(self, y):
        for i in range(len(y)):
            for j in range(len(y[i])):
                y[i][j] = (y[i][j]) * (self.a_max[0] - self.a_min[0]) + self.a_min[0]
        return y

    '''Функция разбивки массивов/списков на n-дневки
    Вход:
    data: list/array
    n: int
    Выход:
    newdata: list
    '''
    def data_split(self, data: list, n: int):
        newdata = []
        for i in range(len(data) - n + 1):
            newdata.append(copy.deepcopy(data[i:i + n]))
        return newdata

    '''Функция чистки массивов от несоответствий годов в fd- и fh-дневках
    Вход:
    x_data: list
    y_data: list
    x: array
    y: array
    Выход:
    x_data: list
    y_data: list
    x: array
    y: array
    (Размер входных и выходных массивов отличается)
    '''
    def clean_new(self, x_data, y_data, x, y):
        i = 0
        while i < len(x_data):
            years = [j[0][0:4] for j in x_data[i]]
            years += [j[0][0:4] for j in y_data[i]]
            years = list(set(years))
            if len(years) != 1:
                x_data.pop(i)
                y_data.pop(i)
                x.pop(i)
                y.pop(i)
            else:
                i += 1
        return x_data, y_data, x, y

    '''Функция чтения из xlsx формата и выборки данных по заданным параметрам, также заполняет пропущенные даты для последующего восстановления
    Вход:
    filename: str
    Выход:
    dfs: pandas.DataFrame
    '''
    def xlsx_read(self, filename):
        # Чтение из xlsx формата
        dfs = pd.read_excel(filename, sheet_name='Уровни', engine='openpyxl')
        dfs = dfs[dfs['Код поста'] == int(self.params['hydropost'])]
        dfs = dfs.sort_values('Дата - время')

        pd.options.display.max_columns = None
        pd.options.display.max_rows = None

        dfs['Дата - время'] = pd.to_datetime(dfs['Дата - время'])
        if self.params['merge_missing_dates'] == 'on':
            m1 = dfs['Дата - время'].min()
            m2 = dfs['Дата - время'].max()
            dfs = dfs.set_index('Дата - время')
            dfs = dfs.reindex(pd.date_range(m1, m2)).fillna(np.nan)
        else:
            dfs = dfs.set_index('Дата - время').fillna(np.nan)
        return dfs

    '''Функция получения основных данных из датафрейма:train массивов (multiple, single), массива дат и train массивов с вшитой датой (multiple_dates, single_dates)
    Вход:
    dfs: pandas.DataFrame
    Выход:
    multiple_restored: array
    single: array
    dates: list
    multiple_restored_dates: list
    single_dates: list
    '''
    def get_data_new(self, dfs):
        cols = self.params['selectedcols'].split(',')
        df_multiple = dfs[cols]
        dates = dfs.index.astype('str').values.tolist()

        print('Проверка введенных данных..')
        if self.params['end_date'] not in dates:
            print('Указанной даты нет в файле.')
            exit(0)
        else:
            if dates.index(self.params['end_date']) + int(self.params['fd']) >= len(dates):
                print('Конец датафрейма приходится на конец документа, завершение работы..')
                exit(0)
            print('Все в порядке, происходит обработка')
        # Обрезка всех массивов по дате конца датафрейма + fd дней
        index = dates.index(self.params['end_date'])
        multiple = df_multiple.values.tolist()
        multiple = np.array(multiple)
        if self.params['restore_data'] == 'iter':
            multiple_restored = iter(multiple).tolist()
        elif self.params['restore_data'] == 'knn':
            multiple_restored = knn(multiple, 31).tolist()
        elif self.params['restore_data'] == 'mean':
            multiple_restored = mean(multiple).tolist()
        elif self.params['restore_data'] == 'naive_bayes':
            multiple_restored = naive_bayes(multiple, dates)
        elif self.params['restore_data'] == 'smart_random':
            multiple_restored = smart_random(dfs, self.selected_cols)[self.selected_cols].values.tolist()
        else:
            multiple_restored = idle(multiple).tolist()
        single = [i[0] for i in multiple_restored]
        multiple_restored_dates = copy.deepcopy(multiple_restored)
        single_dates = [[i] for i in single]
        day_in_year = [self.data_check(i) for i in dates]

        for i in range(len(multiple_restored)):
            multiple_restored[i].append(day_in_year[i])
            multiple_restored_dates[i].append(day_in_year[i])
            multiple_restored_dates[i].insert(0, dates[i])

        for i in range(len(single_dates)):
            single_dates[i].insert(0, dates[i])
        restored_df = copy.deepcopy(self.df)
        cutted_df = pd.DataFrame(np.array(multiple_restored))
        cutted_df.index = dates
        new_cols = self.selected_cols + ['День в году']
        cutted_df.columns = new_cols
        restored_df.index = dates
        restored_df[new_cols]=cutted_df[new_cols]
        self.restored_df = restored_df
        if self.params['save_restored_data'] == 'on':
            print('[Восстановление данных] Включена запись восстановленных данных, идет запись...')
            file_format = '.xlsx'
            name = "restored_data " + datetime.datetime.strftime(datetime.datetime.now(), f"%d-%m-%Y %H-%M-%S {self.params['restore_data']}") + file_format
            restored_df.to_excel(name)
            print(f'[Восстановление данных] Восстановленные данные [{len(restored_df)} строк] были записаны в файл {name}')
        single_dates = single_dates[int(self.params['fh']):]
        single = single[int(self.params['fh']):]
        multiple_restored = multiple_restored[:index+1]
        multiple_restored_dates = multiple_restored_dates[:index+1]
        return multiple_restored, single, dates, multiple_restored_dates, single_dates

    '''Функция формировки кубов из подготовленных данных
    Вход:
    multiple_restored: array
    single: array
    multiple_restored_dates: list
    single_dates: list
    Выход:
    x: array
    y: array
    x_data: list
    y_data: list
    '''
    def cube_formation(self, multiple_restored, single, multiple_restored_dates, single_dates):
        x = copy.deepcopy(self.data_split(multiple_restored, int(self.params['fh'])))
        y = copy.deepcopy(self.data_split(single, int(self.params['fd'])))
        x_data = copy.deepcopy(self.data_split(multiple_restored_dates, int(self.params['fh'])))
        y_data = copy.deepcopy(self.data_split(single_dates, int(self.params['fd'])))
        y_data = y_data[:len(x_data)]
        y = y[:len(x)]
        return x, y, x_data, y_data

    '''Функция подсчета номера дня в году по дате
    Вход:
    date: str (формат: YYYY-MM-DD)
    Выход:
    summ: int (min=1, max=365)
    '''
    def data_check(self, date: str):
        summ = 0
        month_dict = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31,
        }
        dlist = date.split('-')
        for i in range(1, int(dlist[1])):
            summ += month_dict[i]
        summ += int(dlist[-1])
        return summ

# Создание объекта класса Data
obj = Data('Urovni2_1_1_new.xlsx')
x, y = obj.x, obj.y
x_data, y_data = obj.x_data, obj.y_data
dates = obj.dates