import configparser
import matplotlib.pyplot as plt


# Булата
def index_search(data, date):
    for days in data:
        if days[-1][0] == date:
            return data.index(days)

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
