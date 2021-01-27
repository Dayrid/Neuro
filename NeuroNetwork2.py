import numpy as np
import os
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.layers import Dense, LSTM, GRU
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import RMSprop, Adam
from tensorflow.keras.utils import normalize
from PM import x, y, y_data, dates
from buf import index_search
import configparser
import tensorflow as tf




# Булат
def cfg():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    mas = dict(config.items('Settings'))
    return mas


# функция построения графика процесса обучения
def plot_train_history(history, title):
    loss = history.history['mae']
    val_loss = history.history['val_mae']

    epochs = range(len(loss))

    plt.figure()

    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title(title)
    plt.legend()

    plt.show()


settings = cfg()
first = np.array(x).reshape(len(x), int(settings['fh']), len(x[0][0]))
copy = x
second = np.array(y).reshape(len(y), int(settings['fd']))
first = normalize(first)
second /= 1000
model = Sequential()

model.add(LSTM(int(settings['inputunits']), return_sequences=True, input_shape=(int(settings['fh']), len(first[0][0]))))
model.add(LSTM(int(settings['hideunits']), activation=settings['activationfuncinhidelayer']))
# model.add(Dense(32, activation='sigmoid'))
model.add(Dense(int(settings['fd']), activation=settings['activationfuncinoutputlayer']))

model.compile(loss=settings['funcerror'], optimizer=Adam(float(settings['h'])), metrics=['mae'])

history = model.fit(first, second, epochs=int(settings['epoch']), batch_size=int(settings['batchsize']),
                    validation_split = float(settings['validationsize']))

plot_train_history(history, "График")

ind = index_search(y_data, settings['end_date'])
print(ind, ' ', settings['end_date'])

predict_result = model.predict(np.array(first[ind]).reshape(1, int(settings['fh']), len(first[0][0])))

A, B = [], []
prev = []

for i in range(int(settings['fd'])):
    A.append(second[ind][i]*1000)

for i in range(int(settings['fh'])):
    prev.append(copy[ind][i][0])

for i in predict_result[0]:
    B.append(i*1000)

ind = dates.index(settings['end_date']) - int(settings['fh']) - 1
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
#plt.show()

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
