import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from plot_curves import get_extraction_matrix
import os
import sys


def func_exp(x, a, b, c):
    return a*np.exp(b*x) + c


def func_poly(x: list, *coefficients) -> list:
    return sum([c*x**i for i, c in enumerate(coefficients)])


def curve_fitting_poly(x: list, y: list, degree: int) -> tuple:
    scale = 1 / np.max(x)
    x_scaled = x * scale
    initial_guess = [0] + [1] * degree
    params, _ = curve_fit(func_poly, x_scaled, y, p0=initial_guess)
    return [c_scale * (scale**i) for i, c_scale in enumerate(params)]


def calculate_x_axis(iterations, timestep=60):
    duration = iterations * timestep / 86400
    x = np.linspace(0, duration, iterations)
    return x


def sum_of_square_error(func, params, experiment_data_file, data_number=3):
    with open(experiment_data_file, "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        experiment_data = experiment_data[0:data_number]

    x = experiment_data[0]
    print(f"x:\n{x}")
    y = func(x, *params)

    sse = np.sum((y - experiment_data[1]*0.01)**2)
    return sse


def calculate_all_sse(extraction_matrix, config_json, experiment_data_file):
    for extraction in extraction_matrix:
        print(f"Processing k:{extraction['k']} phi: {extraction['phi']}")
        iterations = len(extraction["Cu_extraction"])
        step = iterations // config_json["data_numbers_to_fit"]
        x = calculate_x_axis(iterations, config_json["timestep"])

        x = x[::step]
        data_point = extraction["Cu_extraction"][::step]

        params = curve_fitting_poly(
            x, data_point, config_json["polynomial_degree"])

        extraction["sse"] = sum_of_square_error(
            func_poly, params, experiment_data_file, config_json["experiment_data_number"])
    df = pd.DataFrame(extraction_matrix)
    print(f"sse:\n{df['sse']}")

    return df


def validate_setting_keys(setting_json):
    required_keys = ["experiment_data_number", "data_numbers_to_fit", "polynomial_degree",
                     "timestep", "save_path", "show_plot", "x_axis"]
    missing = [key for key in required_keys if key not in setting_json]
    if missing:
        return False, f"Missing setting keys: {missing}"
    return True, None


def main():
    with open("../config/sum_of_square_error.json", "r") as f:
        config_json = json.load(f)

    key_validated, missing_message = validate_setting_keys(config_json)
    if not key_validated:
        print(missing_message)
        sys.exit(1)

    with open("../config/plot_curves.json", "r") as f:
        experiment_data_file = json.load(f)["experiment_data_file"]

    try:
        extraction_matrix = get_extraction_matrix()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    df_sse = calculate_all_sse(extraction_matrix, config_json, experiment_data_file)

    save_path = os.path.abspath(config_json["save_path"])
    if save_path:
        with open(save_path, "w") as f:
            df_sse.to_csv(f)

    x_axis = config_json["x_axis"]
    if config_json["show_plot"]:
        fig, ax = plt.subplots()
        ax.scatter(df_sse[x_axis], df_sse["sse"])
        ax.set_xlabel(f"{str(x_axis)}")
        ax.set_ylabel("Sum of square")
        plt.show()


if __name__ == '__main__':
    main()
