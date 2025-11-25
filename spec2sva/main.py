import argparse
import json
import os

import time

from spec2sva.gram2temp import Gram2Temp
from spec2sva.temp2prop import Temp2Prop
from spec2sva.smtchecker import SMTChecker

def read_json_file(file_path):
    assert os.path.isfile(file_path), f"File not found: {file_path}"
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def write_json_file(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def main():
    ### Main function with command line interface ###

    # Command line argument parser
    parser = argparse.ArgumentParser(description='')
    #parser.add_argument('-o', '--output-dir', type=str, default='.', help='Output directory')

    subparsers = parser.add_subparsers(dest='command', help='Sub-commands: g2t (grammar to templates), t2p (templates to filtered properties), all (full pipeline)')

    # Shared argument: output directory
    shared_parser = argparse.ArgumentParser(add_help=False)
    shared_parser.add_argument('-o', '--output-dir', type=str, default='.', help='Output directory')
    shared_parser.add_argument('--verbose', action='store_true', help='Store intermediate results')
    
    # Sub-command: g2t
    parser_g2t = subparsers.add_parser('g2t', parents=[shared_parser], help='Convert grammar to templates')
    parser_g2t.add_argument('-g', '--grammar', type=str, required=True, help='Grammar file')

    # Sub-command: t2p
    parser_t2p = subparsers.add_parser('t2p', parents=[shared_parser], help='Generate candidate properties and perform SAT-based filtering')
    parser_t2p.add_argument('-t', '--templates', type=str, required=True, help='Template file')
    parser_t2p.add_argument('-w', '--timing-diagrams', type=str, required=True, help='Timing diagrams file')
    
    # Sub-command: all
    parser_all = subparsers.add_parser('all', parents=[shared_parser], help='Full pipeline: grammar to templates, templates to candidate properties, and SAT-based filtering')
    parser_all.add_argument('-g', '--grammar', type=str, required=True, help='Grammar file')
    parser_all.add_argument('-w', '--timing-diagrams', type=str, required=True, help='Timing diagrams file')
    
    args = parser.parse_args()

    # Create output directory
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Execute
    if args.command == 'g2t':
        grammar = read_json_file(args.grammar)
        
        # Grammar-based template generation
        g2t = Gram2Temp(grammar)
        templates = g2t.getTemplates()
        print(f"Tempates: {len(templates)}")
        
        write_json_file(f"{args.output_dir}/templates.json", templates)
        write_json_file(f"{args.output_dir}/templates_NL.json", g2t.getTemplates_NL())

    elif args.command == 't2p':
        templates = read_json_file(args.templates)
        tds_info = read_json_file(args.timing_diagrams)

        # Template-based property generation
        t2p = Temp2Prop(tds_info['signals'], templates)
        candid_props = t2p.getProperties()

        if args.verbose:
            write_json_file(f"{args.output_dir}/candidates.json", candid_props)
            write_json_file(f"{args.output_dir}/candidates_NL.json", t2p.getProperties_NL())
            write_json_file(f"{args.output_dir}/candidates_SVA.json", t2p.getProperties_SVA())
        
        # SAT-based property filtering
        start_time = time.perf_counter()
        smtchecker = SMTChecker(tds_info, candid_props)
        end_time = time.perf_counter()
        print(f"Filtering time: {end_time - start_time:.6f} seconds")
        filtered_props = smtchecker.getProperties()

        # Write the SAT-filtered properties
        write_json_file(f"{args.output_dir}/sat_filtered.json", filtered_props)
        write_json_file(f"{args.output_dir}/sat_filtered_NL.json", smtchecker.getProperties_NL())
        write_json_file(f"{args.output_dir}/sat_filtered_SVA.json", smtchecker.getProperties_SVA())
    
    elif args.command == 'all':
        grammar = read_json_file(args.grammar)
        tds_info = read_json_file(args.timing_diagrams)

        # Grammar-based template generation
        g2t = Gram2Temp(grammar)
        templates = g2t.getTemplates()
        print(f"Tempates: {len(templates)}")
        
        if args.verbose:
            write_json_file(f"{args.output_dir}/templates.json", templates)
            write_json_file(f"{args.output_dir}/templates_NL.json", g2t.getTemplates_NL())

        # Template-based property generation
        t2p = Temp2Prop(tds_info['signals'], templates)
        candid_props = t2p.getProperties()

        if args.verbose:
            write_json_file(f"{args.output_dir}/candidates.json", candid_props)
            write_json_file(f"{args.output_dir}/candidates_NL.json", t2p.getProperties_NL())
            write_json_file(f"{args.output_dir}/candidates_SVA.json", t2p.getProperties_SVA())
        
        # SAT-based property filtering
        start_time = time.perf_counter()
        smtchecker = SMTChecker(tds_info, candid_props)
        end_time = time.perf_counter()
        print(f"Filtering time: {end_time - start_time:.6f} seconds")
        filtered_props = smtchecker.getProperties()

        # Write the SAT-filtered properties
        write_json_file(f"{args.output_dir}/sat_filtered.json", filtered_props)
        write_json_file(f"{args.output_dir}/sat_filtered_NL.json", smtchecker.getProperties_NL())
        write_json_file(f"{args.output_dir}/sat_filtered_SVA.json", smtchecker.getProperties_SVA())
