import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn import metrics
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer
from sklearn.naive_bayes import GaussianNB
import datetime
import math
import copy
np.random.seed(7)

def knn(dataset, K):
    kn = KNNImputer(n_neighbors=K)
    kn = kn.fit_transform(dataset)
    return kn


def mean(dataset):
    si = SimpleImputer(missing_values=np.nan, strategy='median', verbose=0)
    si = si.fit(dataset)
    return si.transform(dataset)


def iter(dataset):
    it = IterativeImputer(random_state=0, initial_strategy='median')
    it = it.fit_transform(dataset)
    return it

def naive_bayes(dataset, dates):
    print('[Восстановление данных] Выбранный метод - Наивный байес')
    print('[Восстановление данных] Формирование массивов для обучения модели...')
    single_cutted = []
    last_param_cutted = []
    multiple_cutted = []
    dates_cutted = []

    dataset_np = np.array(dataset)
    data = list(dataset_np.T)
    data = [i.tolist() for i in data]

    dataset = dataset.tolist()
    last_param_full = [data_check(i) for i in dates]
    print('[Восстановление данных] Выборка массивов без пропущенных значений')
    for i in range(len(dataset)):
        flag = False
        for j in dataset[i]:
            if math.isnan(j):
               flag = True
        if not flag:
            multiple_cutted.append(dataset[i])
            last_param_cutted.append(last_param_full[i])
            dates_cutted.append(dates[i])
    print('[Восстановление данных] Формирование обучающей выборки')
    data_cutted_np = np.array(multiple_cutted)
    data_cutted = list(data_cutted_np.T)
    data_cutted = [i.tolist() for i in data_cutted]
    data_restored = []
    for i in range(len(data_cutted)):
        print(f'[Восстановление данных] Восстановление {i+1} столбца из {len(data_cutted)}')
        x = np.array(last_param_cutted).reshape(-1, 1)
        y = np.array(data_cutted[i])
        print(f'[Восстановление данных] Обучение модели на {i+1} столбце значений..')
        model = GaussianNB()
        model.fit(x, y)
        print(f'[Восстановление данных] Предсказание столбца значений по массиву дат..')
        x_new = np.array(last_param_full).reshape(-1, 1)
        data_restored.append(model.predict(x_new).tolist())
    print(f'[Восстановление данных] Заполнение пропущенных значений исходных данных')
    dataset_copy = copy.deepcopy(dataset)
    data_restored_newformat = np.array(data_restored).T
    data_restored_newformat = data_restored_newformat.tolist()
    for i in range(len(dataset_copy)):
        for j in range(len(dataset_copy[i])):
            if math.isnan(dataset_copy[i][j]):
               dataset_copy[i][j] = data_restored_newformat[i][j]
    print(f'[Восстановление данных] Восстановление данных завершено.')
    return dataset_copy
def smart_random(df, restored_cols):
    dates_list = df.index
    dates_list = [str(i).split(' ')[0] for i in dates_list]
    day_num_list = [data_check(i) for i in dates_list]
    day_num_list_train = {}
    data_train = {}
    for col in restored_cols:
        data_train[col]=[]
        day_num_list_train[col]=[]
        for i in range(len(df[col])):
            if not np.isnan(df[col][i]):
                data_train[col].append(df[col][i])
                day_num_list_train[col].append(day_num_list[i])
    for col in restored_cols:
        for i in range(len(df[col])):
            if np.isnan(df[col][i]):
                n = day_num_list[i]
                index = get_indices(day_num_list_train[col], n)
                temp = []
                for j in index:
                    temp.append(data_train[col][j])
                temp = np.array(temp)
                if len(temp) > 1 and abs(temp.min() - temp.max()) > 0:
                    val = np.random.randint(low = temp.min(), high = temp.max())
                elif len(temp) == 1:
                    val = temp.min()*1.1
                else:
                    index = get_indices(day_num_list_train[col], n-1)
                    temp = []
                    for j in index:
                        temp.append(data_train[col][j])
                    val = np.array(temp).min()*0.99
                df.loc[dates_list[i], col] = val
    return df
def idle(dataset):
    dataset = dataset.tolist()
    temp = []
    for i in dataset:
        flag = False
        for j in i:
            if math.isnan(j):
               flag = True
        if not flag:
            temp.append(i)
    dataset = np.array(temp)
    return dataset

def data_check(date: str):
    return int(datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%j"))

def get_indices(lst, el):
	return [i for i in range(len(lst)) if lst[i] == el]
