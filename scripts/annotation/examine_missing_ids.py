"""
Find sonnets whose IDs are not on the final rhyme df,
to analyze reason.
"""

import os
import pandas as pd


rhyme_dfname = os.path.join("../../data/dataframe-all_lem_sets_emos_with_nrc_filt.tsv")
adso_corpus_dir = os.path.join("../../source/cssdo/source_with_rhyme")
disco_corpus_dir = os.path.join("../../source/disco")
ids_to_keep = os.path.join("../../data/ids_to_keep.txt")

# adso is another name for cssdo corpus
adso_ids_in_source = set([x.replace(".xml", "")
                          for x in  os.listdir(adso_corpus_dir)])
disco_ids_in_source = set([x.replace("disco", "s").replace(".xml", "")
                           for x in os.listdir(disco_corpus_dir)])
all_source_ids = adso_ids_in_source.union(disco_ids_in_source)

rhyme_df = pd.read_csv(rhyme_dfname, sep="\t")

ids_in_df = set(rhyme_df['SonnetID'].tolist())

ids_to_keep_as_set = set([x.strip() for x in open(ids_to_keep)])

in_source_not_in_df = all_source_ids.difference(ids_in_df)
diff_with_keep = ids_to_keep_as_set.difference(in_source_not_in_df)

print("# Missing IDs")
for fn in (sorted(diff_with_keep)):
  print(fn)