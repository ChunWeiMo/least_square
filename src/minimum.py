import json
import os
import numpy as np
import pandas as pd
from sum_of_square_error import func_poly, curve_fitting_poly
from matplotlib import pyplot as plt
from scipy.optimize import minimize


def get_data_point():
    try:
        with open("../config/minimum.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Cannot find minimum.json")
        return

    try:
        data_file = config["data_file"]
        x = config["x"]
        y = config["y"]
        bounds = config["bounds"]
    except KeyError as e:
        print(f"Key cannot be found in minimum.json as {e}")
        return
    else:
        print(f"data_file: {data_file}")
        print(f"x: {x}")
        print(f"y: {y}")
        print(f"bounds: {bounds} \n")

    data_file = os.path.abspath(data_file)
    try:
        data = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"{data} not found. Exiting...")
    else:
        return data[x], data[y], [bounds,]


def find_local_minimum(x, y, bounds):
    print("Finding local minimum...")

    params = curve_fitting_poly(x, y, 3)

    x_scale = (x-x.min())/(x.max()-x.min())
    scaled_params = curve_fitting_poly(x_scale, y, 3)
    def objective(x): return func_poly(x, *scaled_params)

    x0 = np.mean(x_scale)

    scaled_bounds_min = (bounds[0][0]-x.min())/(x.max()-x.min())
    scaled_bounds_max = (bounds[0][1]-x.min())/(x.max()-x.min())
    scaled_bounds = [[scaled_bounds_min, scaled_bounds_max]]
    minimum = minimize(objective, x0=x0, bounds=scaled_bounds)

    if minimum.success:
        x_min = minimum.x * (x.max()-x.min())+x.min()
        print("Local minimum is found:")
        print(f"x= {x_min}")
        plt.scatter(x, y, c="blue", label="model")
        plt.scatter(x, func_poly(x, *params), c="red", label="fitted")
        plt.scatter(x_min, func_poly(x_min, *params),
                    c="green", label="minimum")
        plt.legend()
        plt.show()
        return minimum.x
    else:
        print(f"Cannot find a local minimum in bounds")


def main():
    x, y, bounds = get_data_point()
    if x is not None and y is not None and bounds:
        find_local_minimum(x, y, bounds)


if __name__ == '__main__':
    main()
