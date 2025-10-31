import os, csv, sys

path = "data/pets.csv"
if not os.path.exists(path):
    print("File not found:", path); sys.exit(1)

print("Size (bytes):", os.path.getsize(path))
with open(path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        print(i+1, row)
        if i >= 20: break
