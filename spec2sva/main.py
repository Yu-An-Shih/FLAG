import argparse
import json
import os

from spec2sva.temp2prop import Temp2Prop
from spec2sva.smtchecker import SMTChecker

def main():
    ### Main function with command line interface ###

    # Command line argument parser
    parser = argparse.ArgumentParser(description='')

    # Required arguments
    parser.add_argument('-w', '--waveform-info', type=str, required=True, help='Waveform information file')
    parser.add_argument('-t', '--templates', type=str, required=True, help='Template file')

    # Optional arguments
    parser.add_argument('-o', '--output-dir', type=str, default='', help='Output directory')

    args = parser.parse_args()

    # TODO: Logger?

    # Execute
    # TODO: Provide more options?

    assert os.path.isfile(args.waveform_info), f"Waveform information file not found: {args.waveform_info}"
    with open(args.waveform_info, "r") as f:
        waveform_info = json.load(f)

    assert os.path.isfile(args.templates), f"Template file not found: {args.templates}"
    with open(args.templates, "r") as f:
        templates = json.load(f)
    
    t2p = Temp2Prop(waveform_info['signals'], templates)
    candid_props = t2p.getProperties()

    #print("Number of candidate properties:", len(candid_props))

    smtchecker = SMTChecker(waveform_info, candid_props)
    valid_props = smtchecker.getProperties()

    # Write the SMT-checked properties
    with open(f"{args.output_dir}/properties.json", "w") as f:
        json.dump(valid_props, f, indent=4)
    with open(f"{args.output_dir}/properties_NL.json", "w") as f:
        json.dump(smtchecker.getProperties_NL(), f, indent=4)
