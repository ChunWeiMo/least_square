import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
from least_square.plot_curves import get_extraction_matrix
from least_square.plot_curves import ExtractionMap
import sys
from pathlib import Path


def func_exp(x, a, b, c):
    return a * np.exp(b * x) + c


def func_poly(x: list, *coefficients) -> list:
    return sum([c * x**i for i, c in enumerate(coefficients)])


def curve_fitting_poly(x: list, y: list, degree: int) -> tuple:
    scale = 1 / np.max(x)
    x_scaled = x * scale
    initial_guess = [0] + [1] * degree
    params, _ = curve_fit(func_poly, x_scaled, y, p0=initial_guess)
    return [c_scale * (scale**i) for i, c_scale in enumerate(params)]


def calculate_x_axis(iterations, timestep=60):
    """Time in days for each sample: 0, dt, 2dt, ..., (n-1)dt."""
    return np.arange(iterations) * timestep / 86400.0


def load_experiment_data(experiment_data_filename, max_day=None):
    """Load experiment CSV (day, extraction %). Returns days and fraction extraction."""
    data_path = Path.cwd() / "data" / "experiment_data" / experiment_data_filename
    experiment_data = pd.read_csv(data_path, header=None)

    days = experiment_data[0].to_numpy(dtype=float)
    y = experiment_data[1].to_numpy(dtype=float) * 0.01  # % -> fraction

    if max_day is not None:
        mask = days <= float(max_day)
        days = days[mask]
        y = y[mask]

    return days, y


def sum_of_square_error(sim_days, sim_y, exp_days, exp_y):
    """
    Direct sim vs experiment SSE at experiment times.

    Simulation values are linearly interpolated onto experiment days.
    Only experiment points inside the simulation time span are used
    (avoids extrapolation past the last sim sample).
    """
    if len(exp_days) == 0:
        raise ValueError("No experiment points left after filtering (check max_day).")

    t_min = sim_days[0]
    t_max = sim_days[-1]
    mask = (exp_days >= t_min) & (exp_days <= t_max)
    if not np.any(mask):
        raise ValueError(f"No experiment points overlap sim time range [{t_min:.4g}, {t_max:.4g}] days.")

    exp_days = exp_days[mask]
    exp_y = exp_y[mask]
    sim_at_exp_day = np.interp(exp_days, sim_days, sim_y)
    return float(np.sum((sim_at_exp_day - exp_y) ** 2))


def calculate_all_sse(extraction_matrix: ExtractionMap, config_json, experiment_data_file):
    species = config_json.get("data_to_calculate_sse", "extraction_CuII")
    max_day = config_json.get("max_day")
    timestep = config_json["timestep"]

    exp_days, exp_y = load_experiment_data(experiment_data_file, max_day=max_day)
    print(
        f"SSE uses {len(exp_days)} experiment points"
        + (f" with day <= {max_day}" if max_day is not None else "")
        + f" (t in [{exp_days.min():.4g}, {exp_days.max():.4g}])"
    )

    for run in extraction_matrix.runs:
        print(f"Processing run_id: {run.run_id}, k:{run.k}, phi: {run.phi}")
        if species not in run.data:
            raise KeyError(f"Species '{species}' not found in run {run.run_id} data")

        sim_y = run.data[species][0].to_numpy(dtype=float)
        sim_days = calculate_x_axis(len(sim_y), timestep)
        run.sse = sum_of_square_error(sim_days, sim_y, exp_days, exp_y)
        print(f"  sse={run.sse:.6g}")


def validate_setting_keys(setting_json):
    required_keys = [
        "timestep",
        "save_path",
        "show_plot",
        "x_axis",
    ]
    missing = [key for key in required_keys if key not in setting_json]
    if missing:
        return False, f"Missing setting keys: {missing}"
    return True, None


def runs_to_sse_df(extraction_matrix: ExtractionMap) -> pd.DataFrame:
    rows = [
        {
            "run_id": run.run_id,
            "k": run.k,
            "phi": run.phi,
            "sse": run.sse,
        }
        for run in extraction_matrix.runs
    ]
    return pd.DataFrame(rows).sort_values("run_id").reset_index(drop=True)


def main():
    with open("config/sum_of_square_error.json", "r") as f:
        config_json = json.load(f)

    key_validated, missing_message = validate_setting_keys(config_json)
    if not key_validated:
        print(missing_message)
        sys.exit(1)

    with open("config/plot_curves.json", "r") as f:
        experiment_data_file = json.load(f)["experiment_data_file"]

    try:
        extraction_matrix = get_extraction_matrix()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    calculate_all_sse(extraction_matrix, config_json, experiment_data_file)
    df_sse = runs_to_sse_df(extraction_matrix)
    print(f"sse:\n{df_sse}")

    save_path = Path(config_json["save_path"])
    if not save_path.is_absolute():
        save_path = Path.cwd() / save_path
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df_sse.to_csv(save_path, index=False)
    print(f"Saved: {save_path}")

    x_axis = config_json["x_axis"]
    if config_json["show_plot"]:
        fig, ax = plt.subplots()
        ax.scatter(df_sse[x_axis], df_sse["sse"])
        ax.set_xlabel(str(x_axis))
        ax.set_ylabel("Sum of square error")
        title = "SSE"
        if config_json.get("max_day") is not None:
            title += f" (day ≤ {config_json['max_day']})"
        ax.set_title(title)
        plt.show()


if __name__ == "__main__":
    main()
