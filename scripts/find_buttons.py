import re

with open('public/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if '<button' in line or 'btn-' in line:
        if any(w in line.lower() for w in ['simulate', 'analyze', 'reset', 'case', 'incident', 'trail', 'form']):
            print(f"Line {idx}: {line.strip()}")
            # Print next 3 lines
            for j in range(idx, min(idx+4, len(lines))):
                print(f"   + {lines[j].strip()}")
            print("-" * 40)
