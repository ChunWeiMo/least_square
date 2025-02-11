import json
import numpy as np

def generate_input():
    pass

def main():
    with open('config_input.json', 'r') as f:
        input_config = json.load(f)
    
    k_Cci_min, k_Cci_max = input_config["Cci"]["k_Cci1"]
    phi_Cci1_min, phi_Cci1_max = input_config["Cci"]["phi_Cci1"]
    
    k_Cci_boundary = (k_Cci_min, k_Cci_max)
    phi_Cci_boundary = (phi_Cci1_min, phi_Cci1_max)
    generate_input(k_Cci_boundary, phi_Cci_boundary)
    
if __name__ == '__main__':
    main()