import json
import sys

##### Step 1: Upload the protocol specification files #####
# Terminal command: Upload the spec files via Files API
# curl https://api.openai.com/v1/files -H "Authorization: Bearer $OPENAI_API_KEY" -F purpose="user_data" -F file="@<spec_file>.pdf"


##### Step 2: Construct the configuration file #####
# See work/config.json for the configuration file format


##### Step 3: Create the batch input file #####
# Execute this script to create the OpenAPI batch API input file (work/text_extraction_input.jsonl)

# Configurations
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"
model = sys.argv[2] if len(sys.argv) > 2 else "gpt-5-2025-08-07"

config_file = f"{work_dir}/config.json"
batch_input_file = f"{work_dir}/text_extraction_input.jsonl"

# Read the configuration file
with open(config_file, "r") as f:
    config = json.load(f)

# Text extractor
system_instruction = "You are an expert in formal verification of System-on-Chip (SoC) designs. You will be provided with (1) a specification document of an on-chip communication protocol and (2) a textual instruction requiring information of a specific mechanism (e.g., data transfer, device reset, ...) within the protocol. Based on the textual instruction, your task is to extract signal interaction rules of the target mechanism. Provide the extracted information in a simple text format."

# Create the batch in jsonl format
requests = []
for entry in config:
    protocol = entry["protocol"]
    spec_file_id = entry["spec_file_id"]
    instruction = entry["instruction"]
    
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
                            "text": instruction
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


##### Step 4: Query the LLM and retrieve results #####

# Terminal command: Upload the batch input file
# curl https://api.openai.com/v1/files -H "Authorization: Bearer $OPENAI_API_KEY" -F purpose="batch" -F file="@text_extraction_input.jsonl"

# Terminal command: Create the batch
# curl https://api.openai.com/v1/batches -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d '{ "input_file_id": "<input_file_id>", "endpoint": "/v1/responses", "completion_window": "24h" }'

# Terminal command: Retrieve the results
# curl https://api.openai.com/v1/files/<file-xyz123>/content -H "Authorization: Bearer $OPENAI_API_KEY" > text_extraction_output.jsonl
