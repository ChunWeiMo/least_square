import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import json


def get_k_phi_from_folder(folder):
    match = re.search(r"-k([\d.]+)-phi([\d.]+)", folder)
    if match:
        k, phi = map(float, match.groups())
        print(k, phi)
        return k, phi
    return None, None


def sum_of_square_error():
    pass


def calculate_duration(array):
    iteration = len(array)
    try:
        with open("../config/plot_curves.json", "r") as f:
            plot_config = json.load(f)
            timestep = plot_config["timestep"]
    except (FileNotFoundError, KeyError):
        print("Error: plot_curves.json file not found.")
        print("Using default timestep of 60 seconds.")
        timestep = 60
    duration = iteration * timestep / 86400
    return duration


def plot_extraction_curve(extraction_map_Cci):
    extraction_map_Cci = pd.DataFrame(extraction_map_Cci)
    filter_extraction = extraction_map_Cci
    print(filter_extraction)
    Y = filter_extraction["Cu_extraction"].values

    duration = calculate_duration(Y[0])
    X = np.linspace(0, duration, len(Y[0]))
    fig, ax = plt.subplots()
    ax.set_xlabel("Days")
    ax.set_ylabel("Extraction")

    with open("../config/plot_curves.json", "r") as f:
        plot_config = json.load(f)

    with open(plot_config["experiment_data_file"], "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        ax.scatter(experiment_data[0], experiment_data[1]
                   * 0.01, c="red", label="Experiment")

    for curve, k, phi in zip(Y, filter_extraction["k"].values, filter_extraction["phi"].values):
        ax.plot(X, curve, label=f"k={k}, {phi}")
        ax.legend()
    plt.show()


def get_extraction_matrix():
    all_heapsim_results = "../data/all_heapsim_results"
    all_heapsim_results = os.path.join(
        os.path.dirname(__file__), all_heapsim_results)
    all_heapsim_results = os.path.abspath(all_heapsim_results)

    extraction_map = list()

    for folder in os.listdir(all_heapsim_results):
        folder_path = os.path.join(all_heapsim_results, folder)
        Cci_csv_path = os.path.join(folder_path, "overall_extraction_Cci.csv")
        Bbr_csv_path = os.path.join(folder_path, "overall_extraction_Bbr.csv")
        k, phi = get_k_phi_from_folder(folder)
        print(f"Processing k={k}, phi={phi}")

        if not os.path.exists(Cci_csv_path):
            raise FileNotFoundError(
                f"Error: {Cci_csv_path} not found in {folder_path}!")

        if not os.path.exists(Bbr_csv_path):
            raise FileNotFoundError(
                f"Error: {Bbr_csv_path} not found in {folder_path}!")

        with open(Cci_csv_path, "r") as f:
            Cci_extraction = np.array([float(row.strip())
                                       for row in f.readlines()])
        with open(Bbr_csv_path, "r") as f:
            Bbr_extraction = np.array([float(row.strip())
                                       for row in f.readlines()])
        Cu_extraction = 0.4 * Cci_extraction + 0.6 * Bbr_extraction
        extraction_map.append(
            {"k": k, "phi": phi, "Cci_extraction": Cci_extraction, "Bbr_extraction": Bbr_extraction, "Cu_extraction": Cu_extraction})
    return extraction_map


def main():
    extraction_map = get_extraction_matrix()
    plot_extraction_curve(extraction_map)


if __name__ == "__main__":
    main()
