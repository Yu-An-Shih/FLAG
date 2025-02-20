import json
import sys

from smtchecker import SMTChecker

DATA_DIR = '/scratch/gpfs/ys3146/Workspace/spec_to_SVA'
PROP_DIR = f"{DATA_DIR}/candidate_props_AXI"
SMT_DIR = f"{DATA_DIR}/smt_checked_props_AXI"

def main():
    # TODO: command line argument parser (argparse)
    
    # Read the signals and waveforms
    with open("../waveforms/AXI/valid_ready_handshake.json", "r") as f:
        waveform_info = json.load(f)
    
    # Read the candidate properties
    with open(f"{PROP_DIR}/properties.json", "r") as f:
        properties = json.load(f)
    
    # properties_test = []
    # for property in properties:
    #     if property['ltl'] == '(G (Implies (== VALID 0) (F (== VALID 0))))':
    #         properties_test.append(property)
    #     if property['ltl'] == '(G (Implies (And (== VALID 1) (== READY 0)) (X (== VALID 1))))':
    #         properties_test.append(property)
    # with open("properties_test.json", "w") as f:
    #     json.dump(properties_test, f, indent=4)
    
    # sys.exit(0)

    # with open("properties_test.json", "r") as f:
    #     properties_test = json.load(f)

    smtchecker = SMTChecker(waveform_info, properties)
    properties_held = smtchecker.getProperties()
    
    # Write the properties that hold
    with open(f"{SMT_DIR}/properties.json", "w") as f:
        json.dump(properties_held, f, indent=4)
    
    with open(f"{SMT_DIR}/properties_LTL.json", "w") as f:
        json.dump(smtchecker.getProperties_LTL(), f, indent=4)
    
    with open(f"{SMT_DIR}/properties_NL.json", "w") as f:
        json.dump(smtchecker.getProperties_NL(), f, indent=4)


if __name__ == '__main__':
    main()
