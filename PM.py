import csv
import numpy as np
import configparser
import pandas as pd
import math
import sys
import RecoverDataFrame
import copy
from RecoverDataFrame import *
from math import isnan
class Data():
    # Функция чтения конфига (писал Булат)
    def cfg(self):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        mas = dict(config.items('Settings'))
        return mas
    # Конструктор для формировки массивов
    def __init__(self, filename:str):
        self.params = self.cfg()
        self.df = self.xlsx_read(filename)
        self.multiple_restored, self.single, self.dates, self.multiple_restored_dates, self.single_dates = self.get_data_new(self.df)
        self.x, self.y, self.x_data, self.y_data = self.cube_formation(self.multiple_restored, self.single, self.multiple_restored_dates, self.single_dates)
        self.x_data, self.y_data, self.x, self.y = self.clean_new(self.x_data, self.y_data, self.x, self.y)
    # Разбивка на n-дневки
    def normal(self, x):
        a_min = [100000]*len(x[0][0])
        a_max = [-100000]*len(x[0][0])
        for i in range(len(x)):
            for j in range(len(x[i])):
                for k in range(len(x[i][j])):
                    a_min[k]=min(a_min[k], x[i][j][k])
                    a_max[k]=max(a_max[k], x[i][j][k])
        print(a_min)
        print(a_max)
        for i in range(len(x)):
            for j in range(len(x[i])):
                for k in range(len(x[i][j])):
                    x[i][j][k]=(x[i][j][k]-a_min[k])/(a_max[k]-a_min[k])
        for c in x:
            print(c)
    def data_split(self, data:list, n:int):
        newdata = []
        for i in range(len(data)-n+1):
            newdata.append(data[i:i+n])
        return newdata
    # Чистка массива от мусора и соотношение первого массива ко второму
    def clean_new(self, x_data, y_data, x, y):
        i = 0
        while i<len(x_data):
            years = [j[0][0:4] for j in x_data[i]]
            years += [j[0][0:4] for j in y_data[i]]
            years = list(set(years))
            if len(years) != 1:
                x_data.pop(i)
                y_data.pop(i)
                x.pop(i)
                y.pop(i)
            else:
                i+=1
        return x_data, y_data, x, y
    # Фукнция чтения xlsx формата
    def xlsx_read(self, filename):
        # Чтение из xlsx формата
        dfs = pd.read_excel(filename, sheet_name='Уровни', engine='openpyxl')
        dfs = dfs[dfs['Код поста'] == int(self.params['hydropost'])]
        dfs = dfs.sort_values('Дата - время')
        return dfs
    def get_data_new(self, dfs):
        # Разбор на single, mulitple и массив дат dates
        df_multiple = dfs[['Уровень воды', 'Температура воздуха', 'Атмосферное давление', 'Скорость ветра']]
        df_single = dfs[['Уровень воды']]
        df_dates = dfs[['Дата - время']]
        df_dates['Дата - время'] = df_dates['Дата - время'].astype('str')
        dates = df_dates.values.tolist()
        dates = sum(dates, [])
        print('Проверка введенных данных..')
        if self.params['end_date'] not in dates:
            print('Указанной даты нет в файле.')
            exit(0)
        else:
            if dates.index(self.params['end_date'])+int(self.params['fd'])>=len(dates):
                print('Конец датафрейма приходится на конец документа, завершение работы..')
                exit(0)
            print('Все в порядке, происходит обработка')
        # Обрезка всех массивов по дате конца датафрейма + fd дней
        index = dates.index(self.params['end_date'])
        multiple = df_multiple.values.tolist()
        single = df_single['Уровень воды'].values.tolist()
        # Восстановление данных
        multiple = np.array(multiple[:index+1])
        multiple_restored = iter(multiple).tolist()
        multiple_restored_dates = copy.deepcopy(multiple_restored)
        single_dates = [[i] for i in single]
        day_in_year = [self.data_check(i) for i in dates]
        # Добавление даты и
        for i in range(len(multiple_restored_dates)):
            multiple_restored[i].append(day_in_year[i])
            multiple_restored_dates[i].append(day_in_year[i])
            multiple_restored_dates[i].insert(0, dates[i])
        for i in range(len(single_dates)):
            single_dates[i].insert(0, dates[i])
        single_dates = single_dates[int(self.params['fh']):]
        single = single[int(self.params['fh']):]
        return multiple_restored, single, dates, multiple_restored_dates, single_dates
    def cube_formation(self, multiple_restored, single, multiple_restored_dates, single_dates):
        x = self.data_split(multiple_restored, int(self.params['fh']))
        y = self.data_split(single, int(self.params['fd']))
        x_data = self.data_split(multiple_restored_dates, int(self.params['fh']))
        y_data = self.data_split(single_dates, int(self.params['fd']))
        y_data = y_data[:len(x_data)]
        return x, y, x_data, y_data
    def data_append(self, alist: list):
        year = int(alist[0][0].split('-')[0])
        for i in alist:
            i.append(self.data_check(i[0]))
        return alist
    def data_check(self, date:str):
        summ = 0
        month_dict = {
            1:31,
            2:28,
            3:31,
            4:30,
            5:31,
            6:30,
            7:31,
            8:31,
            9:30,
            10:31,
            11:30,
            12:31,
            }
        dlist = date.split('-')
        for i in range(1, int(dlist[1])):
            summ += month_dict[i]
        summ += int(dlist[-1])
        if summ >= 365:
            summ -= 365
        return summ
# Создание объекта класса Data
obj = Data('Urovni2_1_1_new.xlsx')
x,y = obj.x, obj.y
x_data, y_data = obj.x_data, obj.y_data
dates = obj.dates
print(len(x_data), len(y_data))
for c in x_data:
    print(c)
for c in y_data:
    print(c)