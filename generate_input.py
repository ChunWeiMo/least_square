import json
import numpy as np


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
    if args[0] == "r_Cci1":
        print("Generating input for Cci...")
        k_Cci_boundary = args[1]["k_Cci1"]
        k_Cci_sample = np.linspace(
            k_Cci_boundary[0], k_Cci_boundary[1], k_Cci_boundary[2])

        phi_Cci_boundary = args[1]["phi_Cci1"]
        phi_Cci_sample = np.linspace(
            phi_Cci_boundary[0], phi_Cci_boundary[1], phi_Cci_boundary[2])
        k_Cci, phi_Cci = np.meshgrid(k_Cci_sample, phi_Cci_sample)
        Cci_sample = np.column_stack((np.ravel(k_Cci), np.ravel(phi_Cci)))

        with open("Cci_sample.csv", "w") as f:
            f.write("k_Cci,phi_Cci\n")
            for row in Cci_sample:
                f.write("{},{}\n".format(row[0], row[1]))


def main():
    with open('generate_input_config.json', 'r') as f:
        print("Reading input configuration...") 
        input_config = json.load(f)

    for species, parameters in input_config.items():
        generate_input(species, parameters)


if __name__ == '__main__':
    main()
