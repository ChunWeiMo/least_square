import subprocess
import os
import json
import shutil


def get_heapsim_paths():
    heapsim_dir = os.path.join(os.path.dirname(__file__), "../heapsim")
    heapsim_dir = os.path.abspath(heapsim_dir)
    if not os.path.exists(heapsim_dir):
        raise FileNotFoundError(f"Error: {run_sh_path} not found!")

    run_sh_path = os.path.join(os.path.dirname(__file__), "../heapsim/run.sh")
    run_sh_path = os.path.abspath(run_sh_path)
    if not os.path.exists(run_sh_path):
        raise FileNotFoundError(f"Error: {run_sh_path} not found!")

    rate_params_path = os.path.join(os.path.dirname(
        __file__), "../heapsim/params/rate_parameters.json")
    rate_params_path = os.path.abspath(rate_params_path)
    if not os.path.exists(rate_params_path):
        raise FileNotFoundError(f"Error: {rate_params_path} not found!")

    result_path = os.path.join(os.path.dirname(
        __file__), "../heapsim/results/CSV")
    result_path = os.path.abspath(result_path)
    if result_path is None:
        raise FileNotFoundError(f"Error: {result_path} not found!")

    return heapsim_dir, run_sh_path, rate_params_path, result_path


def copy_heapsim_results(result_path, simulation_index, rate_data):
    simulation_path = os.path.join(
        "heapsim_results", f"run_{simulation_index:03d}-k{rate_data['k_Cci1']}_phi{rate_data['phi_Cci1']}")
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


def main():
    heapsim_dir, run_sh_path, rate_params_path, result_path = get_heapsim_paths()

    if os.path.exists("heapsim_results"):
        shutil.rmtree("heapsim_results")
    os.makedirs("heapsim_results", exist_ok=True)

    with open('Cci_sample.csv', 'r') as f:
        Cci1_sample = f.readlines()

    simulation_index = 0
    for row in Cci1_sample[1:]:
        row = row.strip().split(',')
        k_Cci1 = float(row[0])
        phi_Cci1 = float(row[1])

        with open(rate_params_path, 'r') as f:
            rate_data = json.load(f)
        rate_data["k_Cci1"] = k_Cci1
        rate_data["phi_Cci1"] = phi_Cci1

        with open(rate_params_path, 'w') as f:
            json.dump(rate_data, f, indent=2)

        # subprocess.run(["bash", run_sh_path, "-n"],
        #                cwd=heapsim_dir, check=True)

        copy_heapsim_results(result_path, simulation_index, rate_data)
        simulation_index += 1


if __name__ == '__main__':
    main()
