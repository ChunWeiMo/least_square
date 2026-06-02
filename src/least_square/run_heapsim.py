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


def get_run_heapsim_config(config_path: Path) -> RunHeapsimConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)
    required_keys = {"samples_file", "k", "phi", "timestep_s", "maxsteps_s"}
    missing_keys = required_keys - set(raw.keys())
    if missing_keys:
        raise KeyError(f"Missing keys: {missing_keys}")

    project_root = Path.cwd()
    samples_path = (project_root / raw["samples_file"]).resolve()
    return RunHeapsimConfig(
        samples_file=samples_path,
        k=str(raw["k"]),
        phi=str(raw["phi"]),
        timestep_s=float(raw["timestep_s"]),
        maxsteps_s=int(raw["maxsteps_s"]),
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
    result_path,
    simulation_index,
    rate_data,
    all_heapsim_results_path,
    k_species,
    phi_species,
):
    simulation_path = os.path.join(
        all_heapsim_results_path,
        f"run_{simulation_index:03d}-k{rate_data[k_species]:.4e}-phi{rate_data[phi_species]:.4e}",
    )
    os.makedirs(simulation_path, exist_ok=True)
    overall_extraction_Cci = os.path.join(result_path, "overall_conversion_Cci.csv")
    overall_extraction_Bbr = os.path.join(result_path, "overall_conversion_Bbr.csv")
    extraction_CuII = os.path.join(result_path, "extraction_CuII.csv")
    if overall_extraction_Cci:
        shutil.copy(overall_extraction_Cci, simulation_path)
        print(f"overall_conversion_Cci.csv copied to {simulation_path}")
    if overall_extraction_Bbr:
        shutil.copy(overall_extraction_Bbr, simulation_path)
        print(f"overall_conversion_Bbr.csv copied to {simulation_path}")
    if extraction_CuII:
        shutil.copy(extraction_CuII, simulation_path)
        print(f"extraction_CuII.csv copied to {simulation_path}")


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
    samples = load_samples(config.samples_file)
    print(f"Loaded {len(samples)} samples from {config.samples_file}")

    params_path = ParamsPath.from_dir(Path.cwd() / "params")
    print(f"rate_params_path: {params_path.rate}")
    print(f"general_params_path: {params_path.general}")
    print(f"enable_features_path: {params_path.enable_features}")

    all_heapsim_results_path = Path.cwd() / "data" / "all_heapsim_results"
    all_heapsim_results_path.mkdir(exist_ok=True)

    simulation_index = 0
    for k, phi in samples:
        print(f"k: {k}, phi: {phi}")
    #     row = row.strip().split(",")
    #     k = float(row[0])
    #     phi = float(row[1])

    #     with open(heapsim_paths["rate_params_path"], 'r') as f:
    #         rate_data = json.load(f)
    #     rate_data[k_species] = k
    #     rate_data[phi_species] = phi

    #     with open(heapsim_paths["rate_params_path"], 'w') as f:
    #         json.dump(rate_data, f, indent=2)

    #     subprocess.run(["bash", "copy_saved_data.sh"],
    #                    cwd=heapsim_paths["heapsim_dir"], check=True)

    #     with open(heapsim_paths["general_params_path"], 'r') as f:
    #         general_param = json.load(f)
    #     general_param["timestep_s"] = 0.1
    #     general_param["maxsteps_s"] = 600
    #     with open(heapsim_paths["general_params_path"], 'w') as f:
    #         json.dump(general_param, f, indent=2)

    #     subprocess.run(["bash", heapsim_paths["run_sh_path"]],
    #                    cwd=heapsim_paths["heapsim_dir"], check=True)

    #     with open(heapsim_paths["general_params_path"], 'r') as f:
    #         general_param = json.load(f)
    #     general_param["timestep_s"] = 1
    #     general_param["maxsteps_s"] = 60
    #     with open(heapsim_paths["general_params_path"], 'w') as f:
    #         json.dump(general_param, f, indent=2)

    #     subprocess.run(["bash", heapsim_paths["run_sh_path"]],
    #                    cwd=heapsim_paths["heapsim_dir"], check=True)

    #     general_param["timestep_s"] = config["timestep_s"]
    #     general_param["maxsteps_s"] = config["maxsteps_s"]
    #     with open(heapsim_paths["general_params_path"], 'w') as f:
    #         json.dump(general_param, f, indent=2)

    #     timer(lambda: subprocess.run(["bash", heapsim_paths["run_sh_path"]],
    #                                  cwd=heapsim_paths["heapsim_dir"], check=True))()

    #     copy_heapsim_results(heapsim_paths["result_path"], simulation_index,
    #                          rate_data, all_heapsim_results_path, k_species, phi_species)
    #     simulation_index += 1


if __name__ == "__main__":
    main()
