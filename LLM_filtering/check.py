import json

case_dir = 'PCI/transactions'

with open(f"{case_dir}/properties_NL.json", "r") as f:
    properties = json.load(f)

with open(f"{case_dir}/results.json", "r") as f:
    results = json.load(f)

with open(f"{case_dir}/targets.json", "r") as f:
    targets = json.load(f)

correct = [item for item in targets if item in results]
missing = [item for item in targets if item not in results]
additional = [item for item in results if item not in targets]
incorrect = [item for item in additional if item in properties]
hallucination = [item for item in additional if item not in properties]

print(f"Correct:")
for item in correct:
    print(item)
print(f"Missing:")
for item in missing:
    print(item)
print(f"Incorrect:")
for item in incorrect:
    print(item)

if len(hallucination) > 0:
    print(f"Hallucination!!!")
    for item in hallucination:
        print(item)
