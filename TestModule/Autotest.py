import configparser
import pandas as pd
import numpy as np
import importlib
import os
from Plotting import *
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
import tensorflow as tf
from tensorflow.keras.models import load_model
pd.options.display.max_columns = None
pd.options.display.max_rows = None
from PM import obj
class Pred:
    def __init__(self):
        import PM
        Data = PM.Data('Urovni2_1_1_new.xlsx')
        config = configparser.ConfigParser()
        config.read("settings.ini")
        settings = dict(config.items('Settings'))
        model = load_model(settings['model_name'])
        x, y, x_data, dates = Data.x, Data.y, Data.x_data, Data.dates
        ind = index_search(x_data, settings['end_date'])
        print(settings['end_date'])

        predict_result = model.predict(np.array(x[ind]).reshape(1, int(settings['fh']), len(x[0][0])))

        self.A, self.B = [], []
        self.prev = []
        x = obj.denormal(x)
        second = obj.denormal_y(y)
        for i in range(int(settings['fd'])):
            self.A.append(second[ind][i])

        for i in range(int(settings['fh'])):
            self.prev.append(x[ind][i][0])

        for i in predict_result[0]:
            self.B.append(i * (obj.a_max[0] - obj.a_min[0]) + obj.a_min[0])

        ind = dates.index(settings['end_date']) - int(settings['fh'])
        one = [dates[ind + i] for i in range(1, int(settings['fh']) + 1)]
        self.two = [dates[ind + i] for i in range(int(settings['fh']) + 1, int(settings['fh']) + int(settings['fd']) + 1)]

        plt.rcParams.update({'font.size': 8})
        plt.figure()
        plt.plot(one, self.prev, self.two, self.B, self.two, self.A)
        plt.legend(('До', 'Прогноз сети', 'Верный ответ'))
        plt.xticks(rotation=35)

        fig, ax = plt.subplots()

        # Скрываем оси
        fig.patch.set_visible(False)
        ax.axis('off')
        ax.axis('tight')

        # Создание и постановка таблиц
        data_table1 = np.rot90(np.array(([self.prev, one])), 3)
        data_table2 = np.rot90(np.array(([self.B, self.two])), 3)
        data_table = np.vstack((data_table1, data_table2))
        ax.table(cellText=data_table, loc='center')

        fig.tight_layout()

        # plt.show()
class Test:
    def __init__(self):
        self.auto_params = self.cfg('Autotest')
        self.df = obj.df[obj.selected_cols[0]]
        begin = obj.dates.index(self.auto_params['data_begin'])
        end = obj.dates.index(self.auto_params['data_last'])
        self.dates = obj.dates[begin:end+1]
        full_dates = obj.dates[begin-int(obj.params['fh']):end+1]
        self.df = self.df.dropna()
        self.df = self.df[self.dates]
        self.df = pd.DataFrame(self.df)
        for i in range(int(obj.params['fh'])):
            self.df[i+1]= np.nan
        print(self.df)
        for i in range(len(full_dates)):
            cfg = configparser.ConfigParser()
            cfg.read('settings.ini')
            cfg.set('Settings', 'end_date', full_dates[i])
            with open('settings.ini', 'w+') as fp:
                cfg.write(fp)
            Predict = Pred()
            for j in range(i, i+len(Predict.two)+1):
                if j > len(full_dates)-1:
                    break
                if full_dates[j] in Predict.two and full_dates[j] in self.dates:
                    ind = Predict.two.index(full_dates[j])
                    self.df.loc[Predict.two[ind], ind+1] = abs(Predict.A[ind]-Predict.B[ind])
        print(self.df)
    def cfg(self, name):
        config = configparser.ConfigParser()
        config.read("settings.ini", encoding="utf-8")
        mas = dict(config.items(name))
        return mas
if __name__ == "__main__":
    test = Test()