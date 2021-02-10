import numpy as np
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from tensorflow.keras.layers import Dense, LSTM, GRU
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import RMSprop, Adam
from tensorflow.keras.utils import normalize
from PM import x, y, x_data, dates, obj
from Plotting import *


settings = cfg()
first = np.array(x).reshape(len(x), int(settings['fh']), len(x[0][0]))

print(first[0])

second = np.array(y).reshape(len(y), int(settings['fd']))
model = Sequential()

model.add(LSTM(int(settings['inputunits']), input_shape=(int(settings['fh']), len(first[0][0])), return_sequences=True))
model.add(LSTM(int(settings['hideunits']), activation=settings['activationfuncinhidelayer'], return_sequences=True))
model.add(LSTM(int(settings['hideunits']), activation='sigmoid', return_sequences=True))
model.add(LSTM(int(settings['hideunits']), activation='sigmoid'))
model.add(Dense(int(settings['fd']), activation=settings['activationfuncinoutputlayer']))

model.compile(loss=settings['funcerror'], optimizer=Adam(float(settings['h'])), metrics=['mae'])

history = model.fit(first, second, epochs=int(settings['epoch']), batch_size=int(settings['batchsize']),
                    validation_split = float(settings['validationsize']))

plot_train_history(history, "График")

ind = index_search(x_data, settings['end_date'])
print(ind, ' ', settings['end_date'])

predict_result = model.predict(np.array(first[ind]).reshape(1, int(settings['fh']), len(first[0][0])))

A, B = [], []
prev = []
x = obj.denormal(x)
second = obj.denormal_y(second)
for i in range(int(settings['fd'])):
    A.append(second[ind][i])

for i in range(int(settings['fh'])):
    prev.append(x[ind][i][0])

for i in predict_result[0]:
    B.append(i*(obj.a_max[0] - obj.a_min[0]) + obj.a_min[0])

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

plt.show()

if input('save ? +\-') == '+':
    model.save('SaveModels/model-2days-beta.h5')

