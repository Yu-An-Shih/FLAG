import json

start_rules = [1, 101, 201, 301, 401, 501, 598, 701, 801, 901, 1001, 1101, 1201, 1301, 1401, 1501, 1601, 1701, 1801, 1901, 2001, 2101, 2201, 2301, 2401]

with open("../sat_filtered_NL.json", "r") as f:
    candidates = json.load(f)

print(f"Total candidates loaded: {len(candidates)}")

candidate_batches = []
for i in range(len(start_rules)):
    start = start_rules[i] - 1
    end = start_rules[i + 1] - 1 if i + 1 < len(start_rules) else len(candidates)
    batch = candidates[start:end]
    candidate_batches.append(batch)

total = 0
for i, batch in enumerate(candidate_batches):
    print(f"Batch {i + 1}: {len(batch)} candidates")
    total += len(batch)
print(f"Total candidates: {total}")

with open("sat_filtered_NL.json", "w") as f:
    json.dump(candidate_batches, f, indent=4)