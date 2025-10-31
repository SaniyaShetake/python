import pandas as pd

pets = pd.read_csv("data/pets.csv")
pets["id"] = range(1, len(pets) + 1)  # make IDs 1,2,3,...
pets.to_csv("data/pets.csv", index=False)
print("✅ Reset pet IDs starting from 1")
