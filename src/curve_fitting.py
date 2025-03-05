import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np


def func_poly(x, *coefficients):
    return sum([c*x**i for i, c in enumerate(coefficients)])


def func_exp(x, a, b, c):
    return a*np.exp(b*x) + c


def calculate_x_axis(array, timestep=60):
    iteration = len(array)
    duration = iteration * timestep / 86400
    x = np.linspace(0, duration, len(array))
    return x


def sum_of_square_error(func, params):
    with open("../data/experiment_data/experiment_data-1ft-full.csv", "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        experiment_data = experiment_data[0:3]

    x = experiment_data[0]
    y = func(x, *params) * 100

    error = np.sum((y - experiment_data[1])**2)
    print(f"Sum of square error: {error}")
    
    fig, ax= plt.subplots()
    ax.plot(x, y, label="Fitted curve")
    ax.scatter(experiment_data[0], experiment_data[1], c="red", label="Experiment")
    ax.legend()
    plt.show()


def main():
    with open("../config/curve_fitting_setting.json", "r") as f:
        setting_json = json.load(f)
        data_point = setting_json["data_point"]
        data_number = setting_json["data_numbers_to_fit"]
        polynomial_degree = setting_json["polynomial_degree"]
        timestep = setting_json["timestep"]
    try:
        data_point = pd.read_csv(data_point, header=None)
    except Exception as e:
        print(f"Error: {e}")
    else:
        step = len(data_point[0]) // data_number
        x = calculate_x_axis(data_point[0], timestep)

        x = x[::step]
        data_point = data_point[0][::step]

        degree = polynomial_degree
        initial_guess = [0] + [1] * degree
        params, _ = curve_fit(func_poly, x, data_point, p0=initial_guess)
        y = func_poly(x, *params)

        sum_of_square_error(func_poly, params)


if __name__ == '__main__':
    main()
