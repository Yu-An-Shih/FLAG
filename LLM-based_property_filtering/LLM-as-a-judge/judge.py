import json
import sys

##### Step 1: Construct the configuration file #####
# See work/config.json for the configuration file format


##### Step 2: Create the batch input file #####
# Execute this script to create the OpenAPI batch API input file (judge_input.jsonl)

# Configurations
work_dir = sys.argv[1] if len(sys.argv) > 1 else "work"
model = sys.argv[2] if len(sys.argv) > 2 else "gpt-5-2025-08-07"

config_file = f"{work_dir}/config.json"
batch_input_file = f"{work_dir}/judge_input.jsonl"

# Read the configuration file
with open(config_file, "r") as f:
    config = json.load(f)

# LLM-as-a-judge
system_instruction = """You are an expert in formal verification of System-on-Chip (SoC) designs. You will be provided with (1) a specification document of an on-chip communication protocol and (2) a list of LLM-generated SVA properties that describes a specific mechanism of the protocol. Categorize each LLM-generated properties with the following step:
1. Irrelevent: Check if the property is not relevant, or does not describe any functionality (e.g., just checking signal width) of the target mechanism.
2. Correct/Incorrect/Possible: For the remaining properties, check whether each of them is correct with respect to the specification document. If a property does not explicitly describe or violate any description from the document, categorize it as Possible.
3. Redundant: For the Correct properties, identify whether each of them is redundant, which means removing them will not affect the functionality of the remaining correct list.
Label each property as either "correct", "redundant", "incorrect", "possible" or "irrelevant" by following the above steps.
Additionally, you will be provided with a manually-developed SVA property list as sample solutions. For each manually developed property, check if its constraint is covered by the LLM-generated list.
"""
system_instruction += """Finally, identify any critical properties, if there's any, that are missing from the both the lists but are necessary to fully describe the target mechanism based on the specification document (description in natural language is fine). Do not try to "strengthen" existing properties by rewriting them. Focus on aspects where the existing properties do not cover."""

# Create the batch in jsonl format
requests = []
for entry in config:
    protocol = entry["protocol"]
    spec_file_id = entry["spec_file_id"]
    # selected_properties = entry["selected_properties"]

    with open(entry["sva_file"], "r") as f:
        sva_properties = f.read()

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
                            "text": sva_properties
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
# curl https://api.openai.com/v1/files -H "Authorization: Bearer $OPENAI_API_KEY" -F purpose="batch" -F file="@judge_input.jsonl"

# Terminal command: Create the batch
# curl https://api.openai.com/v1/batches -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d '{ "input_file_id": "<input_file_id>", "endpoint": "/v1/responses", "completion_window": "24h" }'

# Terminal command: Retrieve the results
# curl https://api.openai.com/v1/files/<file-xyz123>/content -H "Authorization: Bearer $OPENAI_API_KEY" > judge_output.jsonl
