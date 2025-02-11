import subprocess
import os

# run_sh_path = os.path.join(os.path.dirname(__file__), "../heapsim/echo.sh")
run_sh_path = os.path.join(os.path.dirname(__file__), "../heapsim/run.sh")
run_sh_path = os.path.abspath(run_sh_path)
heapsim_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../heapsim"))

if not os.path.exists(run_sh_path):
    raise FileNotFoundError(f"Error: {run_sh_path} not found!")

subprocess.run(["bash", run_sh_path, "-n"], cwd=heapsim_dir, check=True)
