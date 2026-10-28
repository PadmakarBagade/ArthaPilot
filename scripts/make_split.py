import pandas as pd

PATH = "data/private/labeled_raw.csv"   

df = pd.read_csv(PATH)
df = df.drop(columns=["split"], errors="ignore")   # safe to re-run

# ~30% of each category goes to test, so every category is represented
test_idx = df.groupby("true_category").sample(frac=0.30, random_state=42).index
df["split"] = "train"
df.loc[test_idx, "split"] = "test"

df.to_csv(PATH, index=False)

# prints counts only, so you don't see the test rows
print(df["split"].value_counts())
print(pd.crosstab(df["true_category"], df["split"]))