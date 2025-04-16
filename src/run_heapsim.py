import subprocess
import os
import json
import shutil
import time
import logging
import sys
from pathlib import Path


def get_heapsim_paths() -> dict:
    print("Getting HeapSim paths...")
    heapsim_paths = dict()

    heapsim_dir = Path(__file__).parent.parent.parent.joinpath("heapsim")
    if not heapsim_dir.exists():
        raise FileNotFoundError(f"Error: {heapsim_dir} not found!")
    heapsim_paths["heapsim_dir"] = heapsim_dir

    run_sh_path = heapsim_dir.joinpath("run.sh")
    if not run_sh_path.exists():
        raise FileNotFoundError(f"Error: {run_sh_path} not found!")
    heapsim_paths["run_sh_path"] = run_sh_path

    general_params_path = heapsim_dir.joinpath(
        "params", "general_parameters.json")
    if not general_params_path.exists():
        raise FileNotFoundError(f"Error: {general_params_path} not found!")
    heapsim_paths["general_params_path"] = general_params_path

    rate_params_path = heapsim_dir.joinpath("params", "rate_parameters.json")
    if not rate_params_path.exists():
        raise FileNotFoundError(f"Error: {rate_params_path} not found!")
    heapsim_paths["rate_params_path"] = rate_params_path

    result_path = heapsim_dir.joinpath("results", "CSV")
    if not result_path.exists():
        raise FileNotFoundError(f"Error: {result_path} not found!")
    heapsim_paths["result_path"] = result_path

    print("HeapSim paths retrieved successfully!")
    return heapsim_paths


def copy_heapsim_results(result_path, simulation_index, rate_data, all_heapsim_results_path, k_species, phi_species):
    simulation_path = os.path.join(
        all_heapsim_results_path, f"run_{simulation_index:03d}-k{rate_data[k_species]}-phi{rate_data[phi_species]}")
    os.makedirs(simulation_path, exist_ok=True)
    overall_extraction_Cci = os.path.join(
        result_path, "overall_extraction_Cci.csv")
    overall_extraction_Bbr = os.path.join(
        result_path, "overall_extraction_Bbr.csv")
    if overall_extraction_Cci:
        shutil.copy(overall_extraction_Cci, simulation_path)
        print(f"overall_extraction_Cci.csv copied to {simulation_path}")
    if overall_extraction_Bbr:
        shutil.copy(overall_extraction_Bbr, simulation_path)
        print(f"overall_extraction_Bbr.csv copied to {simulation_path}")


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print(f"Execution time: {end - start:.2f} seconds")
    return wrapper


def main():
    heapsim_paths = get_heapsim_paths()

    config_path = Path(__file__).parent.parent.joinpath(
        "config", "run_heapsim.json")
    if not config_path.exists():
        logging.error(f"config file is not found: f{config_path}")
        sys.exit(1)

    with open(config_path, 'r') as f:
        config = json.load(f)
        k_species = config["k"]
        phi_species = config["phi"]

    with open(config['samples_file'], 'r') as f:
        samples = f.readlines()

    all_heapsim_results_path = Path(__file__).parent.parent.joinpath(
        "data", "all_heapsim_results")

    if os.path.exists(all_heapsim_results_path):
        shutil.rmtree(all_heapsim_results_path)
    all_heapsim_results_path.mkdir(exist_ok=True)

    simulation_index = 0
    for row in samples[1:]:
        row = row.strip().split(',')
        k = float(row[0])
        phi = float(row[1])

        with open(heapsim_paths["rate_params_path"], 'r') as f:
            rate_data = json.load(f)
        rate_data[k_species] = k
        rate_data[phi_species] = phi

        with open(heapsim_paths["rate_params_path"], 'w') as f:
            json.dump(rate_data, f, indent=2)

        subprocess.run(["bash", "copy_saved_data.sh"],
                       cwd=heapsim_paths["heapsim_dir"], check=True)

        with open(heapsim_paths["general_params_path"], 'r') as f:
            general_param = json.load(f)
        general_param["timestep_s"] = 1
        general_param["maxsteps_s"] = 60
        with open(heapsim_paths["general_params_path"], 'w') as f:
            json.dump(general_param, f, indent=2)

        subprocess.run(["bash", heapsim_paths["run_sh_path"]],
                       cwd=heapsim_paths["heapsim_dir"], check=True)

        general_param["timestep_s"] = config["timestep_s"]
        general_param["maxsteps_s"] = config["maxsteps_s"]
        with open(heapsim_paths["general_params_path"], 'w') as f:
            json.dump(general_param, f, indent=2)

        timer(lambda: subprocess.run(["bash", heapsim_paths["run_sh_path"]],
                                     cwd=heapsim_paths["heapsim_dir"], check=True))()

        copy_heapsim_results(heapsim_paths["result_path"], simulation_index,
                             rate_data, all_heapsim_results_path, k_species, phi_species)
        simulation_index += 1


if __name__ == '__main__':
    main()
