"""Config for rhyme sentiment tagging with lexical resources"""

import os


# corpus paths

#  to change file names when NRC lexica are used
NRC = True
infix = "_with_nrc" if NRC else ""

df_path = "../../data/dataframe-all.tsv"
#df_path = "../../data/dataframe-disco.tsv"
#df_path = "../../data/dataframe-cssdo.tsv"
df_lem = df_path.replace(".tsv", "_lem.tsv")
df_lem_sets = df_path.replace(".tsv", "_lem_sets.tsv")
df_emos = df_lem_sets.replace(".tsv", f"_emos{infix}.tsv")

# nlp
spacy_model = "es_core_news_sm"
#spacy_model = "es_dep_news_trf"

clitics = ("me", "te", "se", "nos", "os", "vos", "le",
           "lo", "les", "los", "la", "las")

# lexica

lexdir = "../../lexica"
nrc_ei = os.path.join(lexdir, "Spanish-es-NRC-Emotion-Intensity-Lexicon-v1.txt")
nrc_vad = os.path.join(lexdir, "Spanish-es-NRC-VAD-Lexicon.txt")
mlsenticon = "../../lexica/senticon.es.xml"
stadthagen = "../../lexica/13428_2015_700_MOESM1_ESM_stadthagen_vad.csv"
stadthagen_emos = "../../lexica/13428_2017_962_MOESM1_ESM_stadthagen_2018_emos.csv"

emonames = sorted({"anger", "anticipation", "disgust", "fear", "joy", "sadness",
                   "surprise", "trust"})

vadnames = sorted({"valence", "arousal", "dominance"})

# to have common column names for all data
stadthagen_renamer = {"ValenceMean": "valence", "ArousalMean": "arousal"}
stadthagen_emos_renamer = {"Happiness_Mean": "joy", "Disgust_Mean": "disgust",
                           "Anger_Mean": "anger", "Fear_Mean": "fear",
                           "Sadness_Mean": "sadness", }

# coverage files
df_coverage_path = f"../../data/coverage{infix}.tsv"

# signatures (e.g. valence signature)
df_sig_path = f"../../data/signatures{infix}.tsv"
highemo_counts = "../../data/highemos_{}_counts_per_poem.tsv"
if NRC:
  highemo_counts = highemo_counts.replace(".tsv", f"{infix}.tsv")