import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer
from sklearn.linear_model import LogisticRegression
import sys


pd.options.display.max_columns = None
pd.options.display.max_rows = None
sys.setrecursionlimit(100000)


def knn(Dataset, K):
    kn = KNNImputer(n_neighbors=K)
    kn = kn.fit_transform(Dataset)
    return kn


def mean(Dataset):
    si = SimpleImputer(missing_values=np.nan, strategy='median', verbose=0)
    si = si.fit(Dataset)
    return si.transform(Dataset)


def iter(Dataset):
    it = IterativeImputer(random_state=0, initial_strategy='median')
    it = it.fit_transform(Dataset)
    return it


dataset = pd.read_csv('Urovni2_1_1_new.csv', delimiter=';')
df = dataset.head(100)
df = df[['Level Water', 'Temp', 'Atm', 'Speed']]
df = df.iloc[:, :-1].values
print("Data Nan: \n", df)
print("Knn:\n", knn(df, 30))
print("mean:\n", mean(df))
print("Data Nan: \n", df)
print("\n\nIt:\n", iter(df))

