import csv
import numpy as np
import configparser
import pandas as pd
import math
import sys
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
        self.multiple, self.single, self.dates = self.get_data(filename)
        self.md, self.sg, self.dates2 = self.get_data2(filename)
        self.md = self.data_append(self.md)
        self.md_numpy, self.sd_numpy = self.to_np(self.md, self.sg)
        self.multiple = self.data_append(self.multiple)
        self.multiple_splitted = self.data_split(self.multiple, int(self.params['fd']))
        self.single_splitted = self.data_split(self.single, int(self.params['fh']))
        self.multiple_splitted, self.single_splitted = self.clean(self.multiple_splitted, self.single_splitted)
        self.final_first = self.multiple_to_np(self.multiple_splitted)
        self.final_second = self.single_to_np(self.single_splitted)
        pass
    # Функция получения сырого массива значений
    def get_data(self, filename):
        mdata, sdata, data, dates = [], [], [], []
        data = self.xlsx_read(filename)
        print('Проверка корректности данных...')
        check = [i for i in data if i[3] == self.params['end_date'] and not isnan(i[6]) and not isnan(i[7]) and not isnan(i[8])]
        if check == []:
            print(f"Указанной даты {self.params['end_date']} не существует в таблице.")
            self.error = True
            exit(0)
        else:
            print('Все в порядке, происходит обработка данных...')
        for row in data:
            if not isnan(row[6]) and not isnan(row[7]) and not isnan(row[8]):
                mdata.append([row[3], int(row[4]), int(row[6]), int(row[7]), int(row[8])])
                sdata.append([row[3], int(row[4])])
                dates.append(row[3])
            if row[3] == self.params['end_date']:
                i = data.index(row)+1
                mdata.append([row[3], int(row[4]), int(row[6]), int(row[7]), int(row[8])])
                for r in data[i:i+int(self.params['fh'])]:
                    sdata.append([r[3], int(r[4])])
                    if r[3] not in dates:
                        dates.append(r[3])
                break
        return mdata, sdata, dates
    # Разбивка на n-дневки
    def data_split(self, data:list, n:int):
        newdata = []
        for i in range(len(data)-n+1):
            newdata.append(data[i:i+n])
        return newdata
    # Чистка массива от мусора и соотношение первого массива ко второму
    def clean(self, multiple_data:list, single_data:list):
        # Чистка n-дневок от разных годов
        index = []
        ind = 0
        for days in multiple_data:
            years = [i[0][0:4] for i in days]
            years = list(set(years))
            if len(years)!=1:
                index.append(multiple_data.index(days))
        shift = 0
        for i in index:
            del multiple_data[i-shift], single_data[i-shift]
            shift +=1
        if len(multiple_data)>len(single_data[int(self.params['fd']):]):
            multiple_data = multiple_data[len(multiple_data)-len(single_data[int(self.params['fd']):]):]
        elif len(multiple_data)<len(single_data[int(self.params['fd']):]):
            single_data = single_data[len(single_data[int(self.params['fd']):])-len(multiple_data):]
        return multiple_data[:-1], single_data[int(self.params['fd'])+1:]
    # Функции превращения списков в массивы numpy
    def multiple_to_np(self, data:list):
        arr = np.zeros((len(data),int(self.params['fd']),len(data[0][0])-1))
        for i in range(len(data)):
            for j in range(int(self.params['fd'])):
                for k in range(len(data[0][0])-1):
                    arr[i][j][k] = data[i][j][k+1]
        return arr
    def single_to_np(self, data:list):
        arr = np.zeros((len(data),int(self.params['fh'])))
        for i in range(len(data)):
            for j in range(int(self.params['fh'])):
                arr[i][j] = data[i][j][1]
        return arr
    def get_data2(self, filename):
        mdata, sdata, data, dates = [], [], [], []
        data = self.xlsx_read(filename)
        print('Проверка корректности данных...')
        check = [i for i in data if i[3] == self.params['end_date']]
        if check == []:
            print(f"Указанной даты {self.params['end_date']} не существует в таблице.")
            self.error = True
            exit(0)
        else:
            print('Все в порядке, происходит обработка данных...')
        for row in data:
            mdata.append([row[3], row[4], row[6], row[7], row[8]])
            sdata.append([row[3], row[4]])
            dates.append(row[3])
            if row[3] == self.params['end_date']:
                i = data.index(row)+1
                mdata.append([row[3], row[4], row[6], row[7], row[8]])
                for r in data[i:i+int(self.params['fh'])]:
                    sdata.append([r[3], r[4]])
                    if r[3] not in dates:
                        dates.append(r[3])
                break
        return mdata, sdata, dates
    def to_np(self, md, sd):
        temp = []
        for i in range(len(md)):
            del md[i][0], sd[i][0]
            if len(sd[i]) == 1:
                temp.append(sd[i][0])
        return md, temp
    # Фукнция чтения xlsx формата
    def xlsx_read(self, filename):
        data = []
        dfs = pd.read_excel(filename, sheet_name='Уровни', engine='openpyxl')
        dfs = dfs[dfs['Код поста'] == int(self.params['hydropost'])]
        dfs = dfs.sort_values('Дата - время')
        val = dfs.values.tolist()
        for v in val:
            row = v
            row[3] = str(v[3].date())
            data.append(row)
        return data
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
        return summ
# Создание объекта класса Data
obj = Data('Urovni2_1_1_new.xlsx')
''' multiple - это данные с 5 параметрами, дата, уровень воды, температура, скорость воздуха;
    single - это данные с 2 параметрами, дата, уровень воды;
    splitted - данные, разбитые на пятидневки;
    final - финальная версия данных, массив numpy без дат
'''
#предварительные данные
multiple = obj.multiple_splitted
single = obj.single_splitted
print(f'Длины массивов: {len(multiple)}, {len(single)}')
#данные без дат
print()
for c in multiple:
    print(c)
print()
for c in single:
    print(c)
first = obj.final_first
second = obj.final_second
dates = obj.dates
params = obj.params
# Неформатированные данные с NaN
md, sd, dates2 = obj.md, obj.sg, obj.dates2
# Неформатированные данные с NaN без дат
md_numpy, sd_numpy = obj.md_numpy, obj.sd_numpy
for c in md_numpy:
    print(c)
