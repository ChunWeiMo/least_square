import json
import numpy as np
import os


def generate_input(*args, **kwargs):
    """
    Description
    -----------
    Generate input for reactions. 

    Note
    ----
    Every parameters has three values:
        1. Lower boundary
        2. Upper boundary
        3. Number of samples
    """
    if args[0] == "r_Cci":
        print("Generating input for Cci...")
        k_Cci_boundary = args[1]["k_Cci1"]
        k_Cci_sample = np.linspace(
            k_Cci_boundary[0], k_Cci_boundary[1], k_Cci_boundary[2])

        phi_Cci_boundary = args[1]["phi_Cci1"]
        phi_Cci_sample = np.linspace(
            phi_Cci_boundary[0], phi_Cci_boundary[1], phi_Cci_boundary[2])

        print("Generating input for Bbr...")
        k_Bbr_boundary = args[1]["k_Bbr"]
        k_Bbr_sample = np.linspace(
            k_Bbr_boundary[0], k_Bbr_boundary[1], k_Bbr_boundary[2])

        phi_Bbr_boundary = args[1]["phi_Bbr"]
        phi_Bbr_sample = np.linspace(
            phi_Bbr_boundary[0], phi_Bbr_boundary[1], phi_Bbr_boundary[2])

        k_Cci, phi_Cci, k_Bbr, phi_Bbr = np.meshgrid(
            k_Cci_sample, phi_Cci_sample, k_Bbr_sample, phi_Bbr_sample)

        Cci_sample = np.column_stack(
            (np.ravel(k_Cci), np.ravel(phi_Cci), np.ravel(k_Bbr), np.ravel(phi_Bbr)))

        samples_path = "../data/samples"
        if not os.path.exists(samples_path):
            os.makedirs(samples_path)
        csv_path = os.path.join(samples_path, "Cci_samples.csv")

        with open(csv_path, "w") as f:
            f.write("k_Cci,phi_Cci,k_Bbr,phi_Bbr\n")
            for row in Cci_sample:
                f.write("{},{},{},{}\n".format(row[0], row[1], row[2], row[3]))
            print(f"Samples saved to {os.path.abspath(csv_path)}")


def main():
    try:
        with open('../config/generate_input_config.json', 'r') as f:
            print("Reading input configuration...")
            input_config = json.load(f)
    except FileNotFoundError:
        print("File not found. Exiting...")
        return

    for species, parameters in input_config.items():
        print(species, parameters)
        generate_input(species, parameters)


if __name__ == '__main__':
    main()
