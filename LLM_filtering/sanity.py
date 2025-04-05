import json
import os

for subdir, _, files in os.walk('./'):
    prop_file = os.path.join(subdir, 'properties_NL.json')
    target_file = os.path.join(subdir, 'targets.json')

    if os.path.exists(prop_file) and os.path.exists(target_file):
        print(f"Checking {subdir}...")

        with open(prop_file, 'r') as f:
            properties = json.load(f)
        with open(target_file, 'r') as f:
            targets = json.load(f)
        
        missing_targets = [target for target in targets if target not in properties]
        if missing_targets:
            print(f"  Missing targets:")
            for target in missing_targets:
                print(f"    {target}")
        else:
            print("  All targets covered.")
