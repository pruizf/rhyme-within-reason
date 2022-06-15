"""Config for rhyme sentiment tagging with lexical resources"""

df_path = "../data/dataframe-all_lem.tsv"
#df_path = "../data/dataframe-disco.tsv"
#df_path = "../data/dataframe-cssdo.tsv"
df_lem = df_path.replace(".tsv", "_lem3.tsv")
spacy_model = "es_core_news_sm"
#spacy_model = "es_dep_news_trf"

clitics = ("me", "te", "se", "nos", "os", "vos", "le",
           "lo", "les", "los", "la", "las")