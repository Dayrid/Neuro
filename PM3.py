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
        self.error = False
        self.params = self.cfg()
        self.multiple, self.single, self.dates = self.get_data(filename)
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
        check = [i for i in data if i[3] == self.params['end_date']]
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
                i = data.index(row)
                mdata.append([row[3], int(row[4]), int(row[6]), int(row[7]), int(row[8])])
                if row[3] not in dates:
                    dates.append(row[3])
                for j in range(i+1, i+1+int(self.params['fd'])):
                    if [data[j][3], int(data[j][4])] not in sdata:
                        sdata.append([data[j][3], int(data[j][4])])
                    if data[j][3] not in dates:
                        dates.append(data[j][3])
                break
        return mdata, sdata, dates
    # Разбивка на n-дневки
    def data_split(self, data:list, n:int):
        counter = 0
        newdata = []
        temp_array = []
        for i in range(len(data)):
            for e in data[i:]:
                if len(data)-i == n:
                    break
                temp_array.append(e)
                counter +=1
                if counter % n == 0:
                    newdata.append(temp_array)
                    temp_array = []
                    break
        return newdata[:-1]
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
        # Если значения fd fh в конфиге разные то первые значения будут с разницей в fd дней, а последнее значение single_data выведет fh дней после конца датафрейма
        if int(self.params['fd']) != int(self.params['fh']):
            temp = single_data[int(self.params['fd']):]
            for t in temp:
                if t[0][0] == multiple_data[:-1][-1][-1][0]:
                    ind = temp.index(t)+2
                    break
            if temp[:ind][-1][0] == multiple_data[:-1][-1][-1][0]:
                ind += 1
            return multiple_data[:-1], temp[:ind]
        # Если fd fh одинаковые, то разница между первыми и последними будет fd дней.
        # Т.е первое значение массива single_data начнется с разрывом в fd дней, последнее значение первого массива кончается на конечной дате, 
        # а последнее значение второго массива начинается со следующего дня конечной даты.
        else:
            if int(self.params['fd'])>=6:
                return multiple_data[:-2], single_data[int(self.params['fd']):-1]
            else:
                return multiple_data[:-1], single_data[int(self.params['fd']):]
    # Функции превращения списков в массивы numpy
    def multiple_to_np(self, data:list):
        arr = np.zeros((len(data),int(self.params['fd']),4))
        for i in range(len(data)):
            for j in range(int(self.params['fd'])):
                for k in range(4):
                    arr[i][j][k] = data[i][j][k+1]
        return arr
    def single_to_np(self, data:list):
        arr = np.zeros((len(data),int(self.params['fh'])))
        for i in range(len(data)):
            for j in range(int(self.params['fh'])):
                arr[i][j] = data[i][j][1]
        return arr
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
