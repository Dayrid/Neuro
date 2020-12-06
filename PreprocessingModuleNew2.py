import csv
import numpy as np
import config as params
class Data():
    def __init__(self, filename:str):
        self.multiple, self.single = self.get_data(filename)
        self.multiple_splitted = self.data_split(self.multiple, params.Fd)
        self.single_splitted = self.data_split(self.single, params.Fh)
        self.multiple_splitted, self.single_splitted = self.clean(self.multiple_splitted, self.single_splitted)
        self.final_first = self.multiple_to_np(self.multiple_splitted)
        self.final_second = self.single_to_np(self.single_splitted)
        pass
    def get_data(self, filename):
        mdata, sdata, data = [], [], []
        data = self.xlsx_read(filename)
        for row in data:
            if row[6] != None and row[7]!=None and row[8]!=None and row[1] == 3000014:
                mdata.append([row[3], int(row[4]), int(row[6]), int(row[7]), int(row[8])])
                sdata.append([row[3], int(row[4])])
            if row[3] == '2020-04-25':
                break
        return mdata[3:], sdata[3:]
    # Разбивка на пятидневки
    def data_split(self, data:list, n:int):
        counter = 0
        newdata = []
        temp_array = []
        for array in data:
            counter += 1
            temp_array.append(array)
            if counter % n == 0:
                newdata.append(temp_array)
                temp_array = []
        return newdata
    # Выборка через один элемент для каждого массива
    def clean(self, multiple_data:list, single_data:list):
        return multiple_data[:-1], single_data[1:]
    # Функции превращения списков в массивы numpy
    def multiple_to_np(self, data:list):
        arr = np.zeros((len(data),params.Fd,4))
        for i in range(len(data)):
            for j in range(params.Fd):
                for k in range(4):
                    arr[i][j][k] = data[i][j][k+1]
        return arr
    def single_to_np(self, data:list):
        arr = np.zeros((len(data),params.Fh))
        for i in range(len(data)):
            for j in range(params.Fh):
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
for c in multiple:
    print(c)
for c in single:
    print(c)
# данные без дат
print('-'*50)
first = obj.final_first
second = obj.final_second