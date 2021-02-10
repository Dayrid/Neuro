import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from tensorflow.keras.models import load_model
import numpy as np
from PM import x, y, x_data, dates, obj
from Plotting import *
from Test import *
import time

config = configparser.ConfigParser()
config.read("settings.ini")
settings = dict(config.items('Settings'))
model = load_model(settings['model_name'])

ind = index_search(x_data, settings['end_date'])
print(ind, ' ', settings['end_date'])

predict_result = model.predict(np.array(x[ind]).reshape(1, int(settings['fh']), len(x[0][0])))

A, B = [], []
prev = []
x = obj.denormal(x)
second = obj.denormal_y(y)
for i in range(int(settings['fd'])):
    A.append(second[ind][i])

for i in range(int(settings['fh'])):
    prev.append(x[ind][i][0])

for i in predict_result[0]:
    B.append(i * (obj.a_max[0] - obj.a_min[0]) + obj.a_min[0])

ind = dates.index(settings['end_date']) - int(settings['fh'])
one = [dates[ind + i] for i in range(1, int(settings['fh']) + 1)]
two = [dates[ind + i] for i in range(int(settings['fh']) + 1, int(settings['fh']) + int(settings['fd']) + 1)]

print(two)
print(A, B)
print(prev)
plt.rcParams.update({'font.size': 8})
plt.figure()
plt.plot(one, prev, two, B, two, A)
plt.legend(('До', 'Прогноз сети', 'Верный ответ'))
plt.xticks(rotation=35)

fig, ax = plt.subplots()

# Скрываем оси
fig.patch.set_visible(False)
ax.axis('off')
ax.axis('tight')

# Создание и постановка таблиц
data_table1 = np.rot90(np.array(([prev, one])), 3)
data_table2 = np.rot90(np.array(([B, two])), 3)
data_table = np.vstack((data_table1, data_table2))
ax.table(cellText=data_table, loc='center')

fig.tight_layout()

# plt.show()
Test(model)