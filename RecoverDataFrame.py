import numpy as np
import math
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer


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