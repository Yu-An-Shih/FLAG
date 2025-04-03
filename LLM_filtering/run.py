import json
import re
import sys

from openai import OpenAI

client = OpenAI()

case_dir = 'Q-Channel/handshake'
iters = 3

# prompt = """
# I am providing you with a textual description of the Q-Channel handshake mechanism. I am also providing you with a list of candidate rules describing signal behaviors. Please extract the rules from the candidate list that best describe the handshake relationship described in the textual description. Output the selected rules in JSON list format.
# """

# prompt = """
# I will provide you with a list of candidate rules describing signal behaviors of an on-chip communication protocol. These candidate rules are generated from timing diagrams in the protocol specification. I will also provide you with a textual description that explains details of the protocol. Please consider the candidate rules one by one and extract those that are correct with respect to the textual description. Please output the selected rules in JSON list format. The select rules must come from the candidate list.
# """

prompt = """
I will provide you with a list of candidate rules describing signal behaviors of an on-chip communication protocol. These candidate rules are generated from timing diagrams in the protocol specification. I will also provide you with a textual description that explains details of the protocol. Please extract the rules from the candidate list that best describe the details in the textual description. The selected rules must come from the candidate list. Please output the selected rules in JSON list format.
"""

with open(f"{case_dir}/properties_NL.json", "r") as f:
    properties = f.read()
prompt += f"\nCandidate rules:\n{properties}\n\n"

with open(f"{case_dir}/description.txt", "r") as f:
    description = f.read()
prompt += description

results = []
for i in range(iters):
    response = client.responses.create(
        model="o1",
        reasoning={"effort": "high"},
        input=[
            # {
            #     "role": "developer",
            #     "content": "You are an expert in on-chip communication protocols. Please extract the rules from the candidate list that best describe the handshake relationship described in the textual description. The select rules must come from the candidate list."
            # },
            {
                "role": "developer",
                "content": "You are an expert in on-chip communication protocols, such as AXI, WISHBONE, APB and PCI."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
    )
    results.append(response.output_text)

with open(f"{case_dir}/results.txt", "w") as f:
    for i, result in enumerate(results):
        f.write(f"Results {i+1}:\n")
        f.write(result)
        f.write("\n==================\n\n\n")


# Extract the rules from the results
num_results = 0
rules = []
with open(f"{case_dir}/results.txt", "r") as f:
    inside_list = False
    for line in f.readlines():
        stripped = line.strip()
        if stripped == '[':
            num_results += 1
            inside_list = True
        elif stripped == ']':
            assert inside_list
            inside_list = False
        elif inside_list:
            cleaned = re.sub(r'^"(.*)"[,]?$', r'\1', stripped)
            if cleaned not in rules:
                rules.append(cleaned)

assert num_results == iters

with open(f"{case_dir}/results.json", "w") as f:
    json.dump(list(rules), f, indent=4)
