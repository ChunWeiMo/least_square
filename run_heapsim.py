import subprocess
import os
import json


def main():
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

    with open('Cci_sample.csv', 'r') as f:
        Cci1_sample = f.readlines()
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

        subprocess.run(["bash", run_sh_path, "-n"],
                       cwd=heapsim_dir, check=True)


if __name__ == '__main__':
    main()
