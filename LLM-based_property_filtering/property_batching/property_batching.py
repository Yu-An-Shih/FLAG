import json
import sys

##### Step 1: Construct the configuration file #####
# See work/config.json for the configuration file format


##### Step 2: Create the batch input file #####
# Execute this script to create the OpenAPI batch API input file (property_batching_input.jsonl)

# Configurations
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"
model = sys.argv[2] if len(sys.argv) > 2 else "gpt-5-2025-08-07"

config_file = f"{work_dir}/config.json"
batch_input_file = f"{work_dir}/property_batching_input.jsonl"

# Read the configuration file
with open(config_file, "r") as f:
    config = json.load(f)

# Create the batch in jsonl format
requests = []
for entry in config:
    protocol = entry["protocol"]
    approx_batch_num = entry["approx_batch_num"]
    max_batch_size = entry["max_batch_size"]
    
    with open(entry["candidates"], "r") as f:
        candidates = json.load(f)
    
    sentences = "\n".join(f"{i+1}. {sentence}" for i, sentence in enumerate(candidates))

    instruction = f"You will receive a list of signal interaction rules. These rules are already ordered by rule structures and signal names. Divide this list into around {approx_batch_num} batches with similar sizes. Try your best to keep similar rules (in terms of rule structure and signal names) in the same batch. The maximum batch size should be within {max_batch_size}. Provide the output as a list of starting rule numbers in each batch (e.g., [1, 101, ...]).\n\nSignal interaction rules:\n{sentences}"

    # Create the batch in jsonl format
    requests.append({
        "custom_id": f"{protocol}: Approximately {approx_batch_num} batches",
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": model,
            "input": [
                {
                    "role": "user",
                    "content": [
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


##### Step 3: Query the LLM and retrieve results #####

# Terminal command: Upload the batch input file
# curl https://api.openai.com/v1/files -H "Authorization: Bearer $OPENAI_API_KEY" -F purpose="batch" -F file="@property_batching_input.jsonl"

# Terminal command: Create the batch
# curl https://api.openai.com/v1/batches -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d '{ "input_file_id": "<input_file_id>", "endpoint": "/v1/responses", "completion_window": "24h" }'

# Terminal command: Retrieve the results
# curl https://api.openai.com/v1/files/<file-xyz123>/content -H "Authorization: Bearer $OPENAI_API_KEY" > property_batching_output.jsonl