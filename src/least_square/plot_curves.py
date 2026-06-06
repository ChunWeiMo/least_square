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


def plot_csv(emap: ExtractionMap, species: str):
    plot_config_json = Path.cwd() / "config" / "plot_curves.json"
    experiment_data_path = Path.cwd() / "data" / "experiment_data"
    if plot_config_json.is_file():
        with open(plot_config_json, "r") as f:
            plot_config = json.load(f)
            experiment_data_file = plot_config.get("experiment_data_file")
            if experiment_data_file:
                experiment_data_path = experiment_data_path / experiment_data_file
            else:
                print("Error: 'experiment_data_file' not found in plot_curves.json.")
                print("Using default path for experiment data.")

    with open(experiment_data_path, "r") as f:
        experiment_data = pd.read_csv(f, header=None)

    with open("config/run_heapsim.json") as f:
        timestep_s = json.load(f)["timestep_s"]

    fig, ax = plt.subplots()
    ax.set_xlabel("Days")
    ax.set_ylabel(species)

    ax.scatter(
        experiment_data[0], experiment_data[1] * 0.01, c="red", label="Experiment"
    )
    
    for run in emap.runs:
        y = run.data[species]

        if hasattr(y, "values"):
            y = y[0].to_numpy()

        n = len(y) - 1
        days = np.linspace(0, n * timestep_s / 86400.0, n)

        ax.plot(
            days,
            y[1:],
            label=f"run={int(run.run_id)}, k={run.k:.2e}, phi={run.phi:.2e}",
        )

    ax.legend()
    plt.title(species)

    output_dir = Path.cwd() / "img"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{species}.png"

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Plot saved to: {output_path}")


def main():
    extraction_map = get_extraction_matrix()

    config_json = Path.cwd() / "config" / "plot_curves.json"
    with open(config_json, "r") as f:
        csv_to_be_plotted = json.load(f)["csv_to_be_plotted"]
    plot_csv(extraction_map, csv_to_be_plotted)


if __name__ == "__main__":
    main()
