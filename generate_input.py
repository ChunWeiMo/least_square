import json
import numpy as np


def generate_input(*args, **kwargs):
    if args[0] == "Cci":
        k_Cci_boundary = args[1]["k_Cci1"]
        k_Cci_sample = np.linspace(k_Cci_boundary[0], k_Cci_boundary[1], 10)

        phi_Cci_boundary = args[1]["phi_Cci1"]
        phi_Cci_sample = np.linspace(
            phi_Cci_boundary[0], phi_Cci_boundary[1], 10)
        k_Cci, phi_Cci = np.meshgrid(k_Cci_sample, phi_Cci_sample)
        Cci_sample = np.column_stack((np.ravel(k_Cci), np.ravel(phi_Cci)))

        with open("Cci_sample.csv", "w") as f:
            f.write("k_Cci,phi_Cci\n")
            for row in Cci_sample:
                f.write("{},{}\n".format(row[0], row[1]))


def main():
    with open('config_input.json', 'r') as f:
        input_config = json.load(f)

    for species, parameters in input_config.items():
        generate_input(species, parameters)


if __name__ == '__main__':
    main()
