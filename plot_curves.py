import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re


def get_k_phi_from_folder(folder):
    match = re.search(r"-k([\d.]+)_phi([\d.]+)", folder)
    if match:
        k, phi = map(float, match.groups())
        return k, phi
    return None, None


def main():
    heapsim_results = "heapsim_results"
    heapsim_results = os.path.join(os.path.dirname(__file__), heapsim_results)
    heapsim_results = os.path.abspath(heapsim_results)

    extraction_map_Cci = list()

    for folder in os.listdir(heapsim_results):
        folder_path = os.path.join(heapsim_results, folder)
        csv_path = os.path.join(folder_path, "overall_extraction_Cci.csv")
        k, phi = get_k_phi_from_folder(folder)
        print(f"Processing k={k}, phi={phi}")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"Error: {csv_path} not found in {folder_path}!")

        with open(csv_path, "r") as f:
            extraction = np.array([float(row.strip())
                                  for row in f.readlines()])
        extraction_map_Cci.append(
            {"k": k, "phi": phi, "extraction": extraction})

    extraction_map_Cci = pd.DataFrame(extraction_map_Cci)
    print(extraction_map_Cci)
    filter_extraction = extraction_map_Cci[(extraction_map_Cci["phi"] == 1.0)]
    print(filter_extraction)
    y = filter_extraction["extraction"].values
    for curve in y:
        plt.plot(curve)
    # plt.show()


if __name__ == "__main__":
    main()
