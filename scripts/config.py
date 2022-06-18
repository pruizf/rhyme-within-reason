"""Config for rhyme sentiment tagging with lexical resources"""

import os


# corpus paths
df_path = "../data/dataframe-all.tsv"
#df_path = "../data/dataframe-disco.tsv"
#df_path = "../data/dataframe-cssdo.tsv"
df_lem = df_path.replace(".tsv", "_lem.tsv")
df_lem_sets = df_path.replace(".tsv", "_lem_sets.tsv")
df_emos = df_lem_sets.replace(".tsv", "_emos7.tsv")

# nlp
spacy_model = "es_core_news_sm"
#spacy_model = "es_dep_news_trf"

clitics = ("me", "te", "se", "nos", "os", "vos", "le",
           "lo", "les", "los", "la", "las")

# lexica

lexdir = "../lexica"
nrc_ei = os.path.join(lexdir, "Spanish-es-NRC-Emotion-Intensity-Lexicon-v1.txt")
nrc_vad = os.path.join(lexdir, "Spanish-es-NRC-VAD-Lexicon.txt")
mlsenticon = "../lexica/senticon.es.xml"
stadthagen = "../lexica/13428_2015_700_MOESM1_ESM_stadthagen_vad.csv"

emonames = sorted({"anger", "anticipation", "disgust", "fear", "joy", "sadness",
                   "surprise", "trust"})

vadnames = sorted({"valence", "arousal", "dominance"})
