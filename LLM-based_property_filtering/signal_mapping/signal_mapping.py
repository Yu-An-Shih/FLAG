import json
import sys

##### Step 1: Construct the configuration file #####
# See work/config.json for the configuration file format

##### Step 2: Create the batch input file #####
# Execute this script to create the OpenAPI batch API input file (signal_mapping_input.jsonl)

# Configurations
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"
model = sys.argv[2] if len(sys.argv) > 2 else "gpt-5-2025-08-07"

config_file = f"{work_dir}/config.json"
batch_input_file = f"{work_dir}/signal_mapping_input.jsonl"

# Read the configuration file
with open(config_file, "r") as f:
    config = json.load(f)

# Signal mapping
system_instruction = "You are an expert in formal verification of System-on-Chip (SoC) designs. You will be provided with (1) a specification document of an on-chip communication protocol and (2) a list of signal interaction rules derived from the protocol. The rules might contain \"conceptual signals\" that may refer to one or more actual signals in the specification document. For each rule, your task is to determine whether it contains conceptual signals, and create corresponding rules by enumerating through all the actual signals for each conceptual signal. Your output should be a list of rules containing only and all the corresponding actual signals. Provide the extracted rules in a JSON list format, without any additional commentary or explanation."

# Create the batch in jsonl format
requests = []
for entry in config:
    protocol = entry["protocol"]
    spec_file_id = entry["spec_file_id"]
    instruction = entry["instruction"] if "instruction" in entry else ""

    with open(entry["rules"], "r") as f:
        rules = json.load(f)

    requests.append({
        "custom_id": protocol,
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": model,
            "instructions": system_instruction,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": spec_file_id
                        },
                        {
                            "type": "input_text",
                            "text": f":{instruction}\n==========\n\nRules:\n{json.dumps(rules, indent=4)}"
                        }
                    ]
                }
            ]
        }
    })

# Write to the jsonl file
with open(batch_input_file, "w") as f:
    for req in requests:
        f.write(json.dumps(req) + "\n")


##### Step 3: Query the LLM and retrieve results #####

# Terminal command: Upload the batch input file
# curl https://api.openai.com/v1/files -H "Authorization: Bearer $OPENAI_API_KEY" -F purpose="batch" -F file="@signal_mapping_input.jsonl"

# Terminal command: Create the batch
# curl https://api.openai.com/v1/batches -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d '{ "input_file_id": "<input_file_id>", "endpoint": "/v1/responses", "completion_window": "24h" }'

# Terminal command: Retrieve the results
# curl https://api.openai.com/v1/files/<file-xyz123>/content -H "Authorization: Bearer $OPENAI_API_KEY" > signal_mapping_output.jsonl
