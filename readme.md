# Least Square Method for HeapSim
## Description
This software is designed to find the best-fitted curves from HeapSim by comparing them with experimental data. The goal is to optimize the parameters of the model to achieve the closest possible match between the simulated and experimental results.

To run the software, ensure it is placed at the same directory level as HeapSim. This allows the software to access HeapSim's functionality and data seamlessly.

### Structure
project_root/
│
├── heapsim/                # HeapSim package
│   ├── build
|   |   └── heapsim         # HeapSim executable
│   ├── src                 # HeapSim source code
│   └── ...                 # Other HeapSim files
│
├── least_square/      # Your software package
│   ├── generate_inputs.py    # Script to generate input data
│   ├── optimize.py           # Script to run the least square method
│   ├── utils/                # Utility functions
│   └── ...                   # Other necessary files
│
├── experiments/              # Experimental data
│   ├── exp_data_1.csv        # Example experimental data file
│   └── ...                   # Other experimental data files
│
└── README.md                 # Project documentation

## Parameters
Different reactions and species have corresponding parameters that can be adjusted to generate the best-fit curve.

### 1st Stage of Ferric Leaching of Chalcocite
* k_Cci1: Reaction rate constant
* phi_Cci1: Topological exponent


