import json

from gram2temp import Gram2Temp

DATA_DIR = '/scratch/gpfs/ys3146/Workspace/spec_to_SVA'

def main():
    # TODO: command line argument parser (argparse)
    
    # Read the grammer
    with open("grammer.json", "r") as f:
        grammer = json.load(f)
    # Get depth information for recursive categories
    with open("depth.json", "r") as f:
        depths = json.load(f)

    g2t = Gram2Temp(grammer, depths)
    templates = g2t.getTemplates()

    # Write the property templates
    with open(f"{DATA_DIR}/templates/templates.json", "w") as f:
        json.dump(templates, f, indent=4)
    
    with open(f"{DATA_DIR}/templates/templates_LTL.json", "w") as f:
        json.dump(g2t.getTemplates_LTL(), f, indent=4)

    with open(f"{DATA_DIR}/templates/templates_NL.json", "w") as f:
        json.dump(g2t.getTemplates_NL(), f, indent=4)

if __name__ == '__main__':
    main()
