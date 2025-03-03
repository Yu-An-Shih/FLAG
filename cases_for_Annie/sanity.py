import json
import os

test_dir = 'complete'

def main():
    for subdir, _, files in os.walk(test_dir):
        prop_file = os.path.join(subdir, 'properties_NL.json')
        target_file = os.path.join(subdir, 'target_props.json')

        if os.path.exists(prop_file) and os.path.exists(target_file):
            print(f"Checking {subdir}...")

            with open(prop_file, 'r') as f:
                properties = json.load(f)
            with open(target_file, 'r') as f:
                targets = json.load(f)
            
            missing_targets = set(targets) - set(properties)
            if missing_targets:
                print(f"  Missing targets:")
                for target in missing_targets:
                    print(f"    {target}")
            else:
                print("  All targets covered.")
            

if __name__ == "__main__":
    main()