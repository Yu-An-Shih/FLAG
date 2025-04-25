import os

for subdir, _, files in os.walk('./'):
    text_file = os.path.join(subdir, 'description.txt')

    if os.path.exists(text_file):
        print(f"Checking {subdir}...")

        with open(text_file, 'r') as f:
            description = f.read()
        
        words = description.split()
        print(f"  Number of words: {len(words)}")
