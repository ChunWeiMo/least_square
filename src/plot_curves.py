import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re


def get_k_phi_from_folder(folder):
    match = re.search(r"-k([\d.]+)_phi([\d.]+)", folder)
    if match:
        k, phi = map(float, match.groups())
        return k, phi
    return None, None


def sum_of_square_error():
    pass


def calculate_duration(array):
    iteration = len(array)
    timestep = 60
    duration = iteration * timestep / 86400
    return duration


def plot_extraction_curve(extraction_map_Cci):
    extraction_map_Cci = pd.DataFrame(extraction_map_Cci)
    filter_extraction = extraction_map_Cci
    print(filter_extraction)
    Y = filter_extraction["extraction"].values

    duration = calculate_duration(Y[0])
    X = np.linspace(0, duration, len(Y[0]))
    fig, ax = plt.subplots()
    ax.set_xlabel("Days")
    ax.set_ylabel("Extraction")

    with open("../data/experiment_data/experiment_data-1ft.csv", "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        ax.scatter(experiment_data[0], experiment_data[1]
                   * 0.01, c="red", label="Experiment")

    for curve, k, phi in zip(Y, filter_extraction["k"].values, filter_extraction["phi"].values):
        ax.plot(X, curve, label=f"k={k}, {phi}")
        ax.legend()
    plt.show()


def get_extraction_matrix():
    heapsim_results_path = "../data/heapsim_results"
    heapsim_results_path = os.path.join(
        os.path.dirname(__file__), heapsim_results_path)
    heapsim_results_path = os.path.abspath(heapsim_results_path)

    extraction_map = list()

    for folder in os.listdir(heapsim_results_path):
        folder_path = os.path.join(heapsim_results_path, folder)
        csv_path = os.path.join(folder_path, "overall_extraction_Cci.csv")
        k, phi = get_k_phi_from_folder(folder)
        print(f"Processing k={k}, phi={phi}")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Error: {csv_path} not found in {folder_path}!")

        with open(csv_path, "r") as f:
            extraction = np.array([float(row.strip())
                                  for row in f.readlines()])
        extraction_map.append(
            {"k": k, "phi": phi, "extraction": extraction})
    return extraction_map


def main():
    extraction_map = get_extraction_matrix()
    plot_extraction_curve(extraction_map)


if __name__ == "__main__":
    main()
