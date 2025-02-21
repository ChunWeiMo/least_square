import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def func(x, a, b, c, d, e, f):
    return a*x**4 + b*x**3 + c*x**2 + d*x + e


def read_experiment_data():
    with open("plot_curves_setting.json", "r") as f:
        experiment_data_file = json.load(f)["experiment_data_file"]

    try:
        experiment_data = pd.read_csv(experiment_data_file, header=None)
        print(experiment_data)
    except Exception as e:
        print(f"Error: {e}")
    else:
        params, _ = curve_fit(func, experiment_data[0], experiment_data[1])
        a, b, c, d, e = params
        print(a, b, c, d)
        X = experiment_data[0]
        y = func(X, a, b, c, d, e)
        print(y)

        fig, ax = plt.subplots()
        ax.plot(X, y)
        ax.scatter(experiment_data[0], experiment_data[1], c="red")
        plt.show()


def main():
    pass


if __name__ == '__main__':
    main()
