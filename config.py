# кол-во эпох
epoch = 150

# функция активации на скрытом слое
activationFuncInHideLayer = 'relu'

# функция активаци на выходном слое
activationFuncInOutputLayer = 'linear'

# размер выборки валидации
validationSize = 0.2

# глубина прогнозирования
Fd = 5

# горизонт прогнозирования
Fh = 5

# Кол-во LSTM блоков во входном слое
inputUnits = 50

# Кол-во LSTM блоков в скрытом слое
hideUnits = 40

# batch size
batchSize = 1

# Функция ошибки
funcError = 'mse'