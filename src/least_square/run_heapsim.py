import subprocess
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


def load_samples(samples_path: Path) -> list[tuple[float, float]]:
    if not samples_path.exists():
        raise FileNotFoundError(f"Samples file not found: {samples_path}")

    with samples_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        return [(float(row[0]), float(row[1])) for row in reader if row]


def _make_run_dir(base: Path, index: int, k: float, phi: float) -> Path:
    """Build the output folder name for one parameter combination."""
    return base / f"run_{index:03d}-k{k:.4e}-phi{phi:.4e}"


def copy_heapsim_results(
    source_dir: Path,
    target_dir: Path,
    filenames: list[str],
) -> None:
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(parents=True)

    for name in filenames:
        src = source_dir / name
        if not src.exists():
            raise FileNotFoundError(f"CSV file not found: {src}")
        shutil.copy(src, target_dir)
        print(f"{name} copied to {target_dir}")


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
    shutil.rmtree(all_heapsim_results_path, ignore_errors=True)
    all_heapsim_results_path.mkdir(parents=True)

    csv_folder_path = Path.cwd() / "result" / "csv"

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
        general_param["timestep_s"] = config.timestep_s
        general_param["maxsteps_s"] = config.maxsteps_s
        with params_path.general.open("w") as f:
            json.dump(general_param, f, indent=2)

        subprocess.run(["heapsim2D"], cwd=Path.cwd(), check=True)

        run_dir = _make_run_dir(all_heapsim_results_path, simulation_index, k, phi)

        copy_heapsim_results(
            csv_folder_path,
            run_dir,
            config.csv_to_be_plotted,
        )
        simulation_index += 1


if __name__ == "__main__":
    main()
