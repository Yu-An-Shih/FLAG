import json

from temp2prop import Temp2Prop

DATA_DIR = '/scratch/gpfs/ys3146/Workspace/spec_to_SVA'

def main():
    # TODO: command line argument parser (argparse)

    # Read the waveform signals
    with open("../waveforms/AXI/valid_ready_handshake.json", "r") as f:
        waveform_info = json.load(f)
        signals = waveform_info['signals']
    
    # Read the templates
    with open(f"{DATA_DIR}/templates/templates.json", "r") as f:
        templates = json.load(f)
    
    t2p = Temp2Prop(signals, templates)
    properties = t2p.getProperties()

    # Write the properties
    with open(f"{DATA_DIR}/candidate_props/properties.json", "w") as f:
        json.dump(properties, f, indent=4)
    
    with open(f"{DATA_DIR}/candidate_props/properties_LTL.json", "w") as f:
        json.dump(t2p.getProperties_LTL(), f, indent=4)

    with open(f"{DATA_DIR}/candidate_props/properties_NL.json", "w") as f:
        json.dump(t2p.getProperties_NL(), f, indent=4)

if __name__ == '__main__':
    main()