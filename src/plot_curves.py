import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import json


def get_k_phi_from_folder(folder):
    match = re.search(
        r"run_(\d+)-k([\d.]+(?:e[-+]?\d+)?)-phi([\d.]+(?:e[-+]?\d+)?)", folder
    )
    if match:
        run, k, phi = map(float, match.groups())
        print(k, phi)
        return run, k, phi
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


def plot_extraction_curve(extraction_map):
    extraction_map = pd.DataFrame(extraction_map)
    filter_extraction = extraction_map
    print(filter_extraction)
    EXT = filter_extraction["Cu_extraction"].values
    CON = filter_extraction["Cu_conversion"].values

    duration = calculate_duration(EXT[0])
    X = np.linspace(0, duration, len(EXT[0]))
    fig, ax = plt.subplots()
    ax.set_xlabel("Days")
    ax.set_ylabel("Extraction")

    with open("../config/plot_curves.json", "r") as f:
        plot_config = json.load(f)

    with open(plot_config["experiment_data_file"], "r") as f:
        experiment_data = pd.read_csv(f, header=None)
        ax.scatter(
            experiment_data[0], experiment_data[1] * 0.01, c="red", label="Experiment"
        )
    
    colors = ['blue','green','red','purple', 'dimgrey']
    for curve, run, k, phi,c in zip(
        EXT,
        filter_extraction["run"],
        filter_extraction["k"].values,
        filter_extraction["phi"].values,
        colors
    ):
        ax.plot(
            X,
            curve,
            label=f"{run} L/hr",
            color=c,
            # label=f"run= {run}, k= {k}, phi= {phi}",
            linestyle="dashed",
        )
        ax.legend()

    for curve, run, k, phi,c in zip(
        CON,
        filter_extraction["run"],
        filter_extraction["k"].values,
        filter_extraction["phi"].values,
        colors
    ):
        ax.plot(
            X,
            curve,
            label=f"{run} L/hr",
            # label=f"run= {run}, k= {k}, phi= {phi}",
            color=c,
            linestyle="solid",
        )
        ax.legend()

    plt.show()


def get_extraction_matrix():
    all_heapsim_results = "../data/all_heapsim_results"
    all_heapsim_results = os.path.join(os.path.dirname(__file__), all_heapsim_results)
    all_heapsim_results = os.path.abspath(all_heapsim_results)

    extraction_map = list()

    for folder in os.listdir(all_heapsim_results):
        folder_path = os.path.join(all_heapsim_results, folder)
        Cci_csv_path = os.path.join(folder_path, "overall_conversion_Cci.csv")
        Bbr_csv_path = os.path.join(folder_path, "overall_conversion_Bbr.csv")
        Cu_csv_path = os.path.join(folder_path, "extraction_CuII.csv")
        run, k, phi = get_k_phi_from_folder(folder)
        print(f"Processing run= {run}, k={k}, phi={phi}")

        if not os.path.exists(Cci_csv_path):
            raise FileNotFoundError(
                f"Error: {Cci_csv_path} not found in {folder_path}!"
            )

        if not os.path.exists(Bbr_csv_path):
            raise FileNotFoundError(
                f"Error: {Bbr_csv_path} not found in {folder_path}!"
            )

        if not os.path.exists(Cu_csv_path):
            raise FileNotFoundError(f"Error: {Cu_csv_path} not found in {folder_path}!")

        with open(Cci_csv_path, "r") as f:
            Cci_conversion = np.array([float(row.strip()) for row in f.readlines()])
        with open(Bbr_csv_path, "r") as f:
            Bbr_conversion = np.array([float(row.strip()) for row in f.readlines()])
        with open(Cu_csv_path, "r") as f:
            Cu_extraction = np.array([float(row.strip()) for row in f.readlines()])

        Cu_conversion = 0.4 * Cci_conversion + 0.6 * Bbr_conversion
        extraction_map.append(
            {
                "run": run,
                "k": k,
                "phi": phi,
                "Cu_conversion": Cu_conversion,
                "Cu_extraction": Cu_extraction,
            }
        )
    return extraction_map


def main():
    extraction_map = get_extraction_matrix()
    plot_extraction_curve(extraction_map)


if __name__ == "__main__":
    main()
