import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import json
from pathlib import Path


class ExtractionMap:
    def __init__(self):
        self.runs = []


class Run:
    def __init__(self, run_id, k, phi):
        self.run_id = run_id
        self.k = k
        self.phi = phi
        self.data = {}


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
        with open("config/plot_curves.json", "r") as f:
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

    with open("config/plot_curves.json", "r") as f:
        plot_config = json.load(f)

    # with open(plot_config["experiment_data_file"], "r") as f:
    #     experiment_data = pd.read_csv(f, header=None)
    #     ax.scatter(
    #         experiment_data[0], experiment_data[1] * 0.01, c="red", label="Experiment"
    #     )

    # colors = ['blue','green','red','purple', 'dimgrey']
    for curve, run, k, phi in zip(
        EXT,
        filter_extraction["run"],
        filter_extraction["k"].values,
        filter_extraction["phi"].values,
    ):
        ax.plot(
            X,
            curve,
            label=f"run= {run}, k= {k}, phi= {phi}",
        )
        ax.legend()

    plt.show()


def get_extraction_matrix():
    all_heapsim_results = Path.cwd() / "data" / "all_heapsim_results"

    emap = ExtractionMap()

    for folder in all_heapsim_results.iterdir():
        if not folder.is_dir():
            continue
        run_id, k, phi = get_k_phi_from_folder(folder.name)
        if run_id is None:
            continue

        run = Run(run_id, k, phi)
        print(f"Processing run= {run.run_id}, k={run.k}, phi={run.phi}")

        for csv_file in os.listdir(folder):
            key = csv_file.split(".")[0]
            csv_data = pd.read_csv(folder / csv_file, header=None)
            run.data[key] = csv_data

        emap.runs.append(run)

    return emap


def main():
    extraction_map = get_extraction_matrix()
    # plot_extraction_curve(extraction_map)


if __name__ == "__main__":
    main()
