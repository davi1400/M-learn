import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
print(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn

from pandas import DataFrame
from matplotlib.colors import ListedColormap

from numpy import where, append, ones, array, zeros, mean, argmax, linspace, concatenate, c_, std
from mlfwk.metrics import metric
from mlfwk.readWrite import load_base
from mlfwk.utils import split_random, get_project_root, normalization, out_of_c_to_label
from mlfwk.models import RadialBasisFunction
from mlfwk.visualization import generate_space, coloring

if __name__ == '__main__':
    print("run abalone")
    final_result = {
        'MSE': [],
        'std MSE': [],
        'RMSE': [],
        'std RMSE': [],
        'R2': [],
        'std R2': [],
        'alphas': []
    }

    results = {
        'realization': [],
        'MSE': [],
        'RMSE': [],
        'R2': [],
        'alphas': []
    }

    # --------------------------- Read dataset ----------------------------------------

    df = load_base('abalone.csv', type='csv')

    # The age of abalone is 1.5 + the rings
    df['age'] = df.Rings + 1.5

    # so after the calculate the age, drop the Rings column
    df.drop('Rings', axis=1, inplace=True)

    # Label enconding of sex feature
    df.Sex = df.Sex.replace({"M": 1, "I": 0, "F": -1})


    df.info()

    features = ['Length', 'Diameter', 'Height', 'Whole weight', 'Shucked weight',
                          'Viscera weight', 'Shell weight', 'Sex']
    target = 'age'

    # -------------------- Realiztions ---------------------------------------------

    # normalizar a base
    df[features] = normalization(df[features], type='min-max')

    N, M = df.shape
    C = 1  # Problema de regressão
    epochs = 10000
    for realization in range(20):
        train, test = split_random(df, train_percentage=.8)
        train, train_val = split_random(train, train_percentage=.8)

        x_train = train[features]
        y_train = train[target].to_numpy().reshape(train[target].shape[0], 1)

        x_train_val = train_val[features]
        y_train_val = train_val[target]


        x_test = test[features]

        y_test = test[target]
        y_test.to_numpy().reshape(y_test.shape[0], 1)

        validation_alphas = [1.0, 1.5, 2.0]
        hidden = [10, 15, 20, 25]
        simple_net = RadialBasisFunction(number_of_neurons=25, N_Classes=1, alpha=1.5, case='regression')
        simple_net.fit(x_train, y_train, x_train_val=x_train_val, y_train_val=y_train_val, alphas=validation_alphas,
                       hidden=hidden)

        y_out = simple_net.predict(x_test, bias=True)

        metrics_calculator = metric(y_test, y_out, types=['MSE', 'RMSE', 'R2'])
        metric_results = metrics_calculator.calculate()
        print(metric_results)

        results['alphas'].append(simple_net.alpha)
        results['realization'].append(realization)
        for type in ['MSE', 'RMSE', 'R2']:
            results[type].append(metric_results[type])


    final_result['alphas'].append(mean(results['alphas']))
    for type in ['MSE', 'RMSE', 'R2']:
        final_result[type].append(mean(results[type]))
        final_result['std ' + type].append(std(results[type]))

    print(pd.DataFrame(final_result))
    pd.DataFrame(final_result).to_csv(
       get_project_root() + '/run/TR-06/ABALONE/results/' + 'result_rbf.csv')


    # ------------------------------------------------------------------------------------




