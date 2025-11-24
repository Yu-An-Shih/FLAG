# Parse the signal mapping results from the OpenAI batch API output file

import json
import sys

# Parameters
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"

batch_output_file = f"{work_dir}/signal_mapping_output.jsonl"
results_json = f"{work_dir}/results.json"
results_txt = f"{work_dir}/results.txt"

with open(batch_output_file, "r") as f:
    responses = [json.loads(line) for line in f]

results = []
for response in responses:
    protocol = response["custom_id"]
    text = response["response"]["body"]["output"][1]["content"][0]["text"]

    # outputs = response["response"]["body"]["output"]
    # message = [out for out in outputs if out["type"] == "message"][0]
    # text = message["content"][0]["text"]
    
    results.append({
        "protocol": protocol,
        "mapped_rules": text
    })

with open(results_json, "w") as f:
    json.dump(results, f, indent=4)

with open(results_txt, "w") as f:
    for entry in results:
        f.write(f"Protocol: {entry['protocol']}\n")
        f.write(f"Mapped rules:\n{entry['mapped_rules']}\n")
        f.write("\n" + "="*80 + "\n\n")
