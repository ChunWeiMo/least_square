import json
import numpy as np
import os
from pathlib import Path


def generate_input(k, phi):
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
    print("Generating input for heapsim...")
    k_sample = np.linspace(k[0], k[1], k[2])
    phi_sample = np.linspace(phi[0], phi[1], phi[2])

    k, phi = np.meshgrid(k_sample, phi_sample)

    samples = np.column_stack((np.ravel(k), np.ravel(phi)))

    samples_path = Path.cwd() / "data/samples"
    if not samples_path.exists():
        samples_path.mkdir(parents=True)

    csv_path = samples_path / "samples.csv"

    with open(csv_path, "w") as f:
        f.write("k,phi\n")
        for row in samples:
            f.write(f"{row[0]:.4e},{row[1]:.4e}\n")
        print(f"Samples saved to {os.path.abspath(csv_path)}")


def main():
    input_config_path = Path.cwd() / "config" / "generate_input_config.json"
    if not input_config_path.exists():
        print("File not found. Exiting...")
        return

    try:
        with open(input_config_path, "r") as f:
            print("Reading input configuration...")
            input_config = json.load(f)
            k = input_config["k"]
            phi = input_config["phi"]
    except FileNotFoundError:
        print("File not found. Exiting...")
        return

    generate_input(k, phi)


if __name__ == "__main__":
    main()
