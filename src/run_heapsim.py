import subprocess
import os
import json
import shutil
import time


def get_heapsim_paths():
    print("Getting HeapSim paths...")
    heapsim_dir = os.path.join(os.path.dirname(__file__), "../../heapsim")
    heapsim_dir = os.path.abspath(heapsim_dir)
    if not os.path.exists(heapsim_dir):
        raise FileNotFoundError(f"Error: {heapsim_dir} not found!")

    run_sh_path = os.path.join(os.path.dirname(
        __file__), "../../heapsim/run.sh")
    run_sh_path = os.path.abspath(run_sh_path)
    if not os.path.exists(run_sh_path):
        raise FileNotFoundError(f"Error: {run_sh_path} not found!")

    general_params_path = os.path.join(os.path.dirname(
        __file__), "../../heapsim/params/general_parameters.json")
    general_params_path = os.path.abspath(general_params_path)
    if not os.path.exists(general_params_path):
        raise FileNotFoundError(f"Error: {general_params_path} not found!")

    rate_params_path = os.path.join(os.path.dirname(
        __file__), "../../heapsim/params/rate_parameters.json")
    rate_params_path = os.path.abspath(rate_params_path)
    if not os.path.exists(rate_params_path):
        raise FileNotFoundError(f"Error: {rate_params_path} not found!")

    result_path = os.path.join(os.path.dirname(
        __file__), "../../heapsim/results/CSV")
    result_path = os.path.abspath(result_path)
    if result_path is None:
        raise FileNotFoundError(f"Error: {result_path} not found!")

    print("HeapSim paths retrieved successfully!")
    return heapsim_dir, run_sh_path, general_params_path, rate_params_path, result_path


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
    heapsim_dir, run_sh_path, general_params_path, rate_params_path, result_path = get_heapsim_paths()

    config_path = os.path.join(os.path.dirname(
        __file__), "../config/run_heapsim.json")

    with open(config_path, 'r') as f:
        config = json.load(f)
        k_species = config["k"]
        phi_species = config["phi"]

    with open(config['samples_file'], 'r') as f:
        samples = f.readlines()

    all_heapsim_results_path = os.path.join(
        os.path.dirname(__file__), "../data/all_heapsim_results")
    if os.path.exists(all_heapsim_results_path):
        shutil.rmtree(all_heapsim_results_path)
    os.makedirs(all_heapsim_results_path, exist_ok=True)

    simulation_index = 0
    for row in samples[1:]:
        row = row.strip().split(',')
        k = float(row[0])
        phi = float(row[1])

        with open(rate_params_path, 'r') as f:
            rate_data = json.load(f)
        rate_data[k_species] = k
        rate_data[phi_species] = phi

        with open(rate_params_path, 'w') as f:
            json.dump(rate_data, f, indent=2)

        subprocess.run(["bash", "copy_saved_data.sh"],
                       cwd=heapsim_dir, check=True)

        with open(general_params_path, 'r') as f:
            general_data = json.load(f)
        general_data["timestep_s"] = 1
        general_data["maxsteps_s"] = 60
        with open(general_params_path, 'w') as f:
            json.dump(general_data, f, indent=2)
        
        subprocess.run(["bash", run_sh_path], cwd=heapsim_dir, check=True)
        
        general_data["timestep_s"] = config["timestep_s"]
        general_data["maxsteps_s"] = config["maxsteps_s"]
        with open(general_params_path, 'w') as f:
            json.dump(general_data, f, indent=2)
        
        timer(lambda: subprocess.run(["bash", run_sh_path],
                                     cwd=heapsim_dir, check=True))()
        
        copy_heapsim_results(result_path, simulation_index,
                             rate_data, all_heapsim_results_path, k_species, phi_species)
        simulation_index += 1


if __name__ == '__main__':
    main()
