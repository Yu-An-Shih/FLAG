import argparse
import json
import os

import time

from spec2sva.gram2temp import Gram2Temp
from spec2sva.temp2prop import Temp2Prop
from spec2sva.smtchecker import SMTChecker

def main():
    ### Main function with command line interface ###

    # Command line argument parser
    parser = argparse.ArgumentParser(description='')
    
    # Input arguments
    #   1. grammar / template set / candidate property set
    #   2. waveform information
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-g', '--grammar', type=str, help='Grammar file')
    group.add_argument('-t', '--templates', type=str, help='Template file')
    group.add_argument('-c', '--candidates', type=str, help='Candidate property file')
    parser.add_argument('-w', '--waveform-info', required=True, type=str, help='Waveform information file')
    
    # Output directory
    parser.add_argument('-o', '--output-dir', type=str, default='.', help='Output directory')

    # Required arguments
    # parser.add_argument('-w', '--waveform-info', type=str, required=True, help='Waveform information file')
    # parser.add_argument('-t', '--templates', type=str, required=True, help='Template file')

    # Optional arguments
    #parser.add_argument('-g', '--grammar', type=str, help='Grammar file')
    #parser.add_argument('-w', '--waveform-info', type=str, help='Waveform information file')
    #parser.add_argument('-t', '--templates', type=str, help='Template file')
    #parser.add_argument('-p', '--properties', type=str, help='Property file')

    #parser.add_argument('-o', '--output-dir', type=str, default='.', help='Output directory')
    
    # TODO: Provide more execution options?
    #parser.add_argument('--g2t', action='store_true', help='Run Gram2Temp only')
    #parser.add_argument('--t2p', action='store_true', help='Run Temp2Prop only')
    #parser.add_argument('--smt', action='store_true', help='Run SMTChecker only')

    args = parser.parse_args()

    # TODO: Logger?

    # Create output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Execute
    assert os.path.isfile(args.waveform_info), f"Waveform information file not found: {args.waveform_info}"
    with open(args.waveform_info, "r") as f:
        waveform_info = json.load(f)
    
    if args.grammar:
        assert os.path.isfile(args.grammar), f"Grammar file not found: {args.grammar}"
        with open(args.grammar, "r") as f:
            grammar = json.load(f)
    elif args.templates:
        assert os.path.isfile(args.templates), f"Template file not found: {args.templates}"
        with open(args.templates, "r") as f:
            templates = json.load(f)
    elif args.candidates:
        assert os.path.isfile(args.candidates), f"Candidate property file not found: {args.candidates}"
        with open(args.candidates, "r") as f:
            candid_props = json.load(f)

    if grammar:
        g2t = Gram2Temp(grammar)
        templates = g2t.getTemplates()

        with open(f"{args.output_dir}/templates.json", "w") as f:
            json.dump(templates, f, indent=4)
        with open(f"{args.output_dir}/templates_NL.json", "w") as f:
            json.dump(g2t.getTemplates_NL(), f, indent=4)

    if templates:
        t2p = Temp2Prop(waveform_info['signals'], templates)
        candid_props = t2p.getProperties()

        # Write the candidate properties
        # with open(f"{args.output_dir}/candid_props.json", "w") as f:
        #     json.dump(candid_props, f, indent=4)
        # with open(f"{args.output_dir}/candid_props_NL.json", "w") as f:
        #     json.dump(t2p.getProperties_NL(), f, indent=4)

    if candid_props:

        start_time = time.perf_counter()
        smtchecker = SMTChecker(waveform_info, candid_props)
        end_time = time.perf_counter()
        print(f"Check time: {end_time - start_time:.6f} seconds")
        valid_props = smtchecker.getProperties()

        # Write the SMT-checked properties
        with open(f"{args.output_dir}/properties.json", "w") as f:
            json.dump(valid_props, f, indent=4)
        with open(f"{args.output_dir}/properties_NL.json", "w") as f:
            json.dump(smtchecker.getProperties_NL(), f, indent=4)
        with open(f"{args.output_dir}/properties_SVA.json", "w") as f:
            json.dump(smtchecker.getProperties_SVA(), f, indent=4)
