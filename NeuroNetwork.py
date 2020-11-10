import numpy as np
import os
import csv
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.utils import normalize

from PreprocessingModule import first
from PreprocessingModule import second


first = np.array(first).reshape(228, 5, 4)
second = np.array(second)

mean = first.mean(axis=0)
std = first.std(axis=0)

first -= mean
first /= std

print(first)

model = Sequential()


model.add(LSTM(30, return_sequences=True, input_shape=(5, 4)))
model.add(LSTM(15, activation='relu'))
model.add(Dense(5, activation='linear'))

model.compile(loss='mse', optimizer=RMSprop(), metrics=['mae'])

history = model.fit(first, second, epochs=200, batch_size=1, validation_split=0.2)

print(model.predict(np.array(first[0]).reshape(1, 5, 4)))
print(second[0])
