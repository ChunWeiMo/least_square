import subprocess
import os
import json
import shutil
import time
import logging
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import csv


@dataclass(frozen=True)
class RunHeapsimConfig:
    samples_file: Path
    k: str
    phi: str
    timestep_s: float
    maxsteps_s: int
    csv_to_be_plotted: list[str]


def get_run_heapsim_config(config_path: Path) -> RunHeapsimConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)
    required_keys = {
        "samples_file",
        "k",
        "phi",
        "timestep_s",
        "maxsteps_s",
        "csv_to_be_plotted",
    }
    missing_keys = required_keys - set(raw.keys())
    if missing_keys:
        raise KeyError(f"Missing keys: {missing_keys}")

    project_root = Path.cwd()
    samples_path = (project_root / raw["samples_file"]).resolve()

    csv_list = raw["csv_to_be_plotted"]
    if not csv_list:
        print("REMINDER: csv_to_be_plotted is empty — no result CSVs will be copied.")

    return RunHeapsimConfig(
        samples_file=samples_path,
        k=str(raw["k"]),
        phi=str(raw["phi"]),
        timestep_s=float(raw["timestep_s"]),
        maxsteps_s=int(raw["maxsteps_s"]),
        csv_to_be_plotted=csv_list or [],
    )


@dataclass(frozen=True)
class ParamsPath:
    general: Path
    rate: Path
    enable_features: Path

    @classmethod
    def from_dir(cls, params_dir: Path) -> "ParamsPath":
        general = params_dir / "general_parameters.json"
        if not general.exists():
            raise FileNotFoundError(f"General parameters not found: {general}")
        rate = params_dir / "rate_parameters.json"
        if not rate.exists():
            raise FileNotFoundError(f"Rate parameters not found: {rate}")
        enable_features = params_dir / "enable_features.json"
        if not enable_features.exists():
            raise FileNotFoundError(f"Enable features not found: {enable_features}")
        return cls(
            general=general,
            rate=rate,
            enable_features=enable_features,
        )


def get_heapsim_paths() -> dict:
    print("Getting HeapSim paths...")
    heapsim_paths = dict()

    heapsim_dir = Path.cwd().parent.joinpath("heapsim2D-python")
    print(heapsim_dir)
    # if not heapsim_dir.exists():
    #     raise FileNotFoundError(f"Error: {heapsim_dir} not found!")
    # heapsim_paths["heapsim_dir"] = heapsim_dir

    # run_sh_path = heapsim_dir.joinpath("run.sh")
    # if not run_sh_path.exists():
    #     raise FileNotFoundError(f"Error: {run_sh_path} not found!")
    # heapsim_paths["run_sh_path"] = run_sh_path

    # general_params_path = heapsim_dir.joinpath(
    #     "params", "general_parameters.json")
    # if not general_params_path.exists():
    #     raise FileNotFoundError(f"Error: {general_params_path} not found!")
    # heapsim_paths["general_params_path"] = general_params_path

    # rate_params_path = heapsim_dir.joinpath("params", "rate_parameters.json")
    # if not rate_params_path.exists():
    #     raise FileNotFoundError(f"Error: {rate_params_path} not found!")
    # heapsim_paths["rate_params_path"] = rate_params_path

    # result_path = heapsim_dir.joinpath("results", "CSV")
    # if not result_path.exists():
    #     raise FileNotFoundError(f"Error: {result_path} not found!")
    # heapsim_paths["result_path"] = result_path

    # print("HeapSim paths retrieved successfully!")
    # return heapsim_paths


def load_samples(samples_path: Path) -> list[tuple[float, float]]:
    if not samples_path.exists():
        raise FileNotFoundError(f"Samples file not found: {samples_path}")

    with samples_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return [(float(row[0]), float(row[1])) for row in reader if row]


def check_params_path():
    params_path = Path.cwd() / "params"
    if not params_path.exists():
        print(f"params folder is not found: {params_path}")
        sys.exit(1)


def copy_heapsim_results(
    csv_folder_path: Path,
    simulation_index: int,
    rate_data: dict[str, Any],
    all_heapsim_results_path: Path,
    config: RunHeapsimConfig,
):
    simulation_path = (
        all_heapsim_results_path
        / f"run_{simulation_index:03d}-k{rate_data[config.k]:.4e}-phi{rate_data[config.phi]:.4e}"
    )
    simulation_path.mkdir(exist_ok=True)
    for csv_file in config.csv_to_be_plotted:
        csv_path = csv_folder_path / csv_file
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        shutil.copy(csv_path, simulation_path)
        print(f"{csv_file} copied to {simulation_path}")


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(f"Execution time: {end - start:.2f} seconds")

    return wrapper


def main():
    config_path = Path.cwd() / "config" / "run_heapsim.json"
    config = get_run_heapsim_config(config_path)
    print(f"csv_to_be_plotted: {config.csv_to_be_plotted}")
    samples = load_samples(config.samples_file)
    print(f"Loaded {len(samples)} samples from {config.samples_file}")
    print(f"k: {config.k}, phi: {config.phi}")

    params_path = ParamsPath.from_dir(Path.cwd() / "params")
    print(f"rate_params_path: {params_path.rate}")
    print(f"general_params_path: {params_path.general}")
    print(f"enable_features_path: {params_path.enable_features}")

    all_heapsim_results_path = Path.cwd() / "data" / "all_heapsim_results"
    all_heapsim_results_path.mkdir(exist_ok=True)

    simulation_index = 0
    for k, phi in samples:
        print(f"k: {k}, phi: {phi}")

        with params_path.rate.open("r") as f:
            rate_data = json.load(f)
        rate_data[config.k] = k
        rate_data[config.phi] = phi
        with open(params_path.rate, "w") as f:
            json.dump(rate_data, f, indent=2)

        with params_path.general.open("r") as f:
            general_param = json.load(f)
        general_param["timestep_s"] = 0.1
        general_param["maxsteps_s"] = 5
        with params_path.general.open("w") as f:
            json.dump(general_param, f, indent=2)

        subprocess.run(["heapsim2D"], cwd=Path.cwd(), check=True)

        csv_folder_path = Path.cwd() / "result" / "csv"

        copy_heapsim_results(
            csv_folder_path,
            simulation_index,
            rate_data,
            all_heapsim_results_path,
            config,
        )
        simulation_index += 1


if __name__ == "__main__":
    main()
