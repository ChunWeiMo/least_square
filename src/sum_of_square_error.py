import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from plot_curves import get_extraction_matrix
import os


def func_exp(x, a, b, c):
    return a*np.exp(b*x) + c


def func_poly(x: list, *coefficients) -> list:
    return sum([c*x**i for i, c in enumerate(coefficients)])


def curve_fitting_poly(x: list, y: list, degree: int) -> tuple:
    initial_guess = [0] + [1] * degree
    params, _ = curve_fit(func_poly, x, y, p0=initial_guess)
    return params


def calculate_x_axis(iterations, timestep=60):
    duration = iterations * timestep / 86400
    x = np.linspace(0, duration, iterations)
    return x


def sum_of_square_error(func, params, experiment_data_file, data_number=3):
    with open("../data/experiment_data/experiment_data-1ft-full.csv", "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        experiment_data = experiment_data[0:data_number]

    x = experiment_data[0]
    print(f"x:\n{x}")
    y = func(x, *params)

    sse = np.sum((y - experiment_data[1]*0.01)**2)
    return sse


def calculate_all_sse(extraction_matrix, polynomial_degree, timestep, save_path, show_plot, x_axis, experiment_data_file, data_number):
    for extraction in extraction_matrix:
        print(f"Processing k:{extraction['k']} phi: {extraction['phi']}")
        iterations = len(extraction["Cu_extraction"])
        step = iterations // data_number
        x = calculate_x_axis(iterations, timestep)

        x = x[::step]
        data_point = extraction["Cu_extraction"][::step]

        params = curve_fitting_poly(x, data_point, polynomial_degree)

        extraction["sse"] = sum_of_square_error(
            func_poly, params, experiment_data_file, data_number)
    df = pd.DataFrame(extraction_matrix)
    print(f"sse:\n{df['sse']}")
    if save_path:
        with open(save_path, "w") as f:
            df.to_csv(f)

    if show_plot:
        fig, ax = plt.subplots()
        ax.scatter(df[x_axis], df["sse"])
        ax.set_xlabel(f"{str(x_axis)}")
        ax.set_ylabel("Sum of square")
        plt.show()


def main():
    with open("../config/sum_of_square_error.json", "r") as f:
        setting_json = json.load(f)
        data_number = setting_json["data_numbers_to_fit"]
        polynomial_degree = setting_json["polynomial_degree"]
        timestep = setting_json["timestep"]
        save_path = setting_json["save_path"]
        save_path = os.path.abspath(save_path)
        show_plot = setting_json["show_plot"]
        x_axis = setting_json["x_axis"]
        data_number = setting_json["experiment_data_number"]

    with open("../config/plot_curves.json", "r") as f:
        experiment_data_file = json.load(f)["experiment_data_file"]

    try:
        extraction_matrix = get_extraction_matrix()
    except Exception as e:
        print(f"Error: {e}")
    else:
        calculate_all_sse(extraction_matrix,
                          polynomial_degree, timestep, save_path, show_plot, x_axis, experiment_data_file, data_number)


if __name__ == '__main__':
    main()
