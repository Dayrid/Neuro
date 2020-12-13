import csv
import numpy as np
import configparser
class Data():
    # Функция чтения конфига (писал Булат)
    def cfg(self):
        config = configparser.ConfigParser()
        config.read("settings.ini")
        mas = dict(config.items('Settings'))
        return mas
    def __init__(self, filename:str):
        self.params = self.cfg()
        self.multiple, self.single, self.dates = self.get_data(filename)
        self.multiple_splitted = self.data_split(self.multiple, int(self.params['fd']))
        self.single_splitted = self.data_split(self.single, int(self.params['fh']))
        self.multiple_splitted, self.single_splitted = self.clean(self.multiple_splitted, self.single_splitted)
        self.final_first = self.multiple_to_np(self.multiple_splitted)
        self.final_second = self.single_to_np(self.single_splitted)
        pass
    def get_data(self, filename):
        mdata, sdata, data, dates = [], [], [], []
        data = self.xlsx_read(filename)
        for row in data:
            if row[6] != None and row[7]!=None and row[8]!=None and row[1] == int(self.params['hydropost']):
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
        return mdata[3:], sdata[3:], dates[3:]
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
    # Выборка через один элемент для каждого массива
    def clean(self, multiple_data:list, single_data:list):
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
        if int(self.params['fd']) != int(self.params['fh']):
            temp = single_data[int(self.params['fd']):]
            for t in temp:
                if t[0][0] == multiple_data[:-1][-1][-1][0]:
                    ind = temp.index(t)+2
                    break
            if temp[:ind][-1][0] == multiple_data[:-1][-1][-1][0]:
                ind += 1
            return multiple_data[:-1], temp[:ind]
        else:
            if int(self.params['fd'])>=7:
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
    def xlsx_read(self, filename):
        from openpyxl import load_workbook
        wb = load_workbook(filename)
        sheet = wb['Уровни']
        rows = sheet.values
        data = []
        for row in rows:
            try:
                temp = []
                date = str(row[3].date())
                for i in range(len(row)):
                    temp.append(row[i])
                temp[3] = date
                data.append(temp)
            except:
                pass
        return data
obj = Data('Urovni2_1_1_new.xlsx')
''' multiple - это данные с 5 параметрами, дата, уровень воды, температура, скорость воздуха;
    single - это данные с 2 параметрами, дата, уровень воды;
    splitted - данные, разбитые на пятидневки;
    final - финальная версия данных, массив numpy без дат
'''
#предварительные данные
multiple = obj.multiple_splitted
single = obj.single_splitted
print(len(multiple), len(single))
#данные без дат
print('-'*100)
for c in multiple:
    print(c)
for c in single:
    print(c)
first = obj.final_first
second = obj.final_second
dates = obj.dates
params = obj.params
