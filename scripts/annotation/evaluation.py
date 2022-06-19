import pandas as pd
df = pd.read_csv('../data/dataframe-all_lem_sets.tsv', sep="\t", low_memory=False)
sample = df.sample(n = 100)
sample.to_csv(r'../data/sample.tsv', sep="\t", mode="a")