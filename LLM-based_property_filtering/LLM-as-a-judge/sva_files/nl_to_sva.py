import json
import sys

# Parameters
work_dir = sys.argv[1] if len(sys.argv) > 1 else "../work"

config_file = f"{work_dir}/config.json"

with open(config_file, "r") as f:
    config = json.load(f)

config_new = []
for entry in config:
    protocol = entry["protocol"].split(" ")[0]
    mechanism = "_".join(entry["protocol"].split(" ")[1:]).replace("-", "_")
    mechanism_name = mechanism.replace("_batching", "")
    
    with open(entry["targets"], "r") as f:
        targets_nl = json.load(f)
    
    with open(entry["rules"], "r") as f:
        llm_filtered_nl = json.load(f)
    
    with open(f"../../../test_cases/{protocol}/{mechanism_name}/sat_filtered.json", "r") as f:
        sat_filtered = json.load(f)
    
    with open(f"{protocol}_{mechanism}.txt", "w") as f:
        f.write(f"// LLM-generated SVA properties for {entry['protocol']}:\n")
        for i, nl_rule in enumerate(llm_filtered_nl):
            rule = next((d for d in sat_filtered if d.get("nl") == nl_rule), None)
            assert rule is not None, f"Rule not found: {nl_rule}"

            f.write(f"// {i+1}. {nl_rule}\n")
            f.write(f"{rule.get('sva')}\n\n")
        
        f.write("\n// Manually-developed SVA properties:\n")
        for i, nl_target in enumerate(targets_nl):
            target = next((d for d in sat_filtered if d.get("nl") == nl_target), None)
            assert target is not None, f"Target not found: {nl_target}"
            f.write(f"// {i+1}. {nl_target}\n")
            f.write(f"{target.get('sva')}\n\n")
    
    entry["sva_file"] = f"sva_files/{protocol}_{mechanism}.txt"
    config_new.append(entry)

with open(config_file, "w") as f:
    json.dump(config_new, f, indent=4)
