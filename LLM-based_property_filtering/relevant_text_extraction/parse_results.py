# Parse the text extraction results from the OpenAI batch API output file
#   Note: The results.json file can be used as the configuration file for the Property Selection Agent

import json
import sys

# Parameters
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"

batch_output_file = f"{work_dir}/text_extraction_output.jsonl"
results_json = f"{work_dir}/results.json"
results_txt = f"{work_dir}/results.txt"

with open(batch_output_file, "r") as f:
    responses = [json.loads(line) for line in f]

textual_descriptions = []
for response in responses:
    id = response["custom_id"]
    text = response["response"]["body"]["output"][1]["content"][0]["text"]

    # outputs = response["response"]["body"]["output"]
    # message = [out for out in outputs if out["type"] == "message"][0]
    # text = message["content"][0]["text"]
    
    protocol = id.split(" ")[0]
    mechanism = "_".join(id.split(" ")[1:]).replace("-", "_")
    
    textual_descriptions.append({
        "protocol": id,
        "candidates": f"../../test_cases/{protocol}/{mechanism}/sat_filtered_NL.json",
        "textual_description": text
    })

with open(results_json, "w") as f:
    json.dump(textual_descriptions, f, indent=4)

with open(results_txt, "w") as f:
    for desc in textual_descriptions:
        f.write(f"Protocol: {desc['protocol']}\n")
        f.write(f"Extracted Textual Description:\n{desc['textual_description']}\n")
        f.write("\n" + "="*80 + "\n\n")
