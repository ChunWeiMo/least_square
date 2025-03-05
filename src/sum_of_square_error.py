import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from plot_curves import get_extraction_matrix


def func_poly(x, *coefficients):
    return sum([c*x**i for i, c in enumerate(coefficients)])


def func_exp(x, a, b, c):
    return a*np.exp(b*x) + c


def calculate_x_axis(iterations, timestep=60):
    duration = iterations * timestep / 86400
    x = np.linspace(0, duration, iterations)
    return x


def sum_of_square_error(func, params):
    with open("../data/experiment_data/experiment_data-1ft-full.csv", "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        experiment_data = experiment_data[0:3]

    x = experiment_data[0]
    y = func(x, *params) * 100

    sse = np.sum((y - experiment_data[1])**2)
    # print(f"Sum of square error: {sse}")
    # fig, ax = plt.subplots()
    # ax.plot(x, y, label="Fitted curve")
    # ax.scatter(experiment_data[0], experiment_data[1],
    #            c="red", label="Experiment")
    # ax.legend()
    # plt.show()
    return sse


def main():
    with open("../config/curve_fitting.json", "r") as f:
        setting_json = json.load(f)
        # data_point = setting_json["data_point"]
        data_number = setting_json["data_numbers_to_fit"]
        polynomial_degree = setting_json["polynomial_degree"]
        timestep = setting_json["timestep"]

    try:
        # data_point = pd.read_csv(data_point, header=None)
        extraction_matrix = get_extraction_matrix()
    except Exception as e:
        print(f"Error: {e}")
    else:
        for extraction in extraction_matrix:
            iterations = len(extraction["Cu_extraction"])
            step = iterations // data_number
            x = calculate_x_axis(iterations, timestep)

            x = x[::step]
            data_point = extraction["Cu_extraction"][::step]

            degree = polynomial_degree
            initial_guess = [0] + [1] * degree
            params, _ = curve_fit(func_poly, x, data_point, p0=initial_guess)
            y = func_poly(x, *params)

            extraction["sse"] = sum_of_square_error(func_poly, params)
        df = pd.DataFrame(extraction_matrix)
        
        fig, ax = plt.subplots()
        ax.scatter(df["k"], df["sse"])
        ax.set_xlabel("k")
        ax.set_ylabel("Sum of square")
        plt.show()        

if __name__ == '__main__':
    main()
