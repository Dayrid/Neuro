import numpy as np
import os
import csv
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import RMSprop, Adam
from tensorflow.keras.utils import normalize

from PreprocessingModule import first
from PreprocessingModule import second

import config as params

# функция построения графика процесса обучения
def plot_train_history(history, title):
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(len(loss))

    plt.figure()

    plt.plot(epochs, loss, 'b', label='Training loss')
    plt.plot(epochs, val_loss, 'r', label='Validation loss')
    plt.title(title)
    plt.legend()

    plt.show()


first = np.array(first).reshape(228, params.Fd, 4)
second = np.array(second)
first = normalize(first)
second /= 1000
model = Sequential()


model.add(LSTM(params.inputUnits, return_sequences=True, input_shape=(params.Fd, 4)))
model.add(LSTM(params.hideUnits, activation=params.activationFuncInHideLayer))
model.add(Dense(params.Fh, activation=params.activationFuncInOutputLayer))

model.compile(loss=params.funcError, optimizer=RMSprop(), metrics=['mae'])

history = model.fit(first, second, epochs=params.epoch, batch_size=params.batchSize, validation_split=params.validationSize)

plot_train_history(history, "График")

print("Пожалуйста, подождите")

true_result = [] # Массив верных результатов
predict_result = [] # Массив прогноза нейросети

# проходим по всем данным, составляя прогноз
for i in range(228):
    A = model.predict(np.array(first[i]).reshape(1, 5, 4))
    for j in range(5):
        true_result.append(second[i][j]*1000)
    for j in A[0]:
        predict_result.append(j*1000)


# строим график
plt.plot(range(len(true_result)), true_result, color='blue', label="Верный ответ")
plt.plot(range(len(true_result)), predict_result, color='red', label="Прогноз")
plt.xlabel("день")
plt.ylabel("Уровень воды")
plt.legend()
plt.show()

