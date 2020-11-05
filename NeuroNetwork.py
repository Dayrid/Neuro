import numpy as np
import os
import csv
import matplotlib.pyplot as plt
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.utils import normalize


model = Sequential()


model.add(LSTM(30, return_sequences=True, input_shape=(5, 4)))
model.add(LSTM(15, activation='relu'))
model.add(Dense(5, activation='linear'))

model.compile(loss='mae', optimizer=RMSprop())

# history = model.fit(x_train, y_train, epochs=1000, validation_data=None)

print(model.get_weights())