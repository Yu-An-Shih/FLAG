import sys

from openai import OpenAI

client = OpenAI()

case_dir = 'Q-Channel/handshake'

# prompt = """
# I am providing you with a textual description of the Q-Channel handshake mechanism. I am also providing you with a list of candidate rules describing signal behaviors. Please extract the rules from the candidate list that best describe the handshake relationship described in the textual description. Output the selected rules in JSON list format.
# """

with open(f"{case_dir}/description.txt", "r") as f:
    description = f.read()
prompt = description

with open(f"{case_dir}/properties_NL.json", "r") as f:
    properties = f.read()
prompt += f"\nCandidate rules:\n{properties}\n"


response = client.responses.create(
    model="o3-mini",
    reasoning={"effort": "medium"},
    input=[
        {
            "role": "user", 
            "content": prompt
        }
    ]
)

with open(f"{case_dir}/results.json", "w") as f:
    f.write(response.output_text)
