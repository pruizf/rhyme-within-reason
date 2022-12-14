"""
Sonnets contained in both CSSDO and DISCO will only be analyzed as part of CSSDO.
This script filters the dataframes to keep the data for CSSDO only.
Duplicate list based on https://github.com/pruizf/disco-ms/blob/master/data/filenames_disco_only.txt
Those IDs were converted to DISCO v3 IDs. CSSDO IDs were added to the list.
"""

import os
import pandas as pd

datadir = "../../data"

ids_to_keep_fn = os.path.join(datadir, "ids_to_keep.txt")

orig_emo_df_fn = os.path.join(datadir, "dataframe-all_lem_sets_emos_with_nrc.tsv")
orig_emo_df_fn_without_nrc = os.path.join(datadir, "dataframe-all_lem_sets_emos.tsv")
orig_highemo_df_fn = os.path.join(datadir, "highemos_06_counts_per_poem_with_nrc.tsv")
orig_highemo_df_fn_without_nrc = os.path.join(datadir, "highemos_06_counts_per_poem.tsv")
# Note: naming logic is the opposite in the data and in this script (with/without nrc)
signatures_fn = os.path.join(datadir, "signatures_with_nrc.tsv")
signatures_fn_without_nrc = os.path.join(datadir, "signatures.tsv")

with open(ids_to_keep_fn, mode="r", encoding="utf8") as idfh:
  ids_to_keep = set([ll.strip() for ll in idfh])

# original dataframes
orig_emo_df = pd.read_csv(orig_emo_df_fn, sep="\t")
orig_highemo_df = pd.read_csv(orig_highemo_df_fn, sep="\t")
orig_emo_df_without_nrc = pd.read_csv(orig_emo_df_fn_without_nrc, sep="\t")
orig_highemo_df_without_nrc = pd.read_csv(orig_highemo_df_fn_without_nrc, sep="\t")
signatures_df = pd.read_csv(signatures_fn, sep="\t")
signatures_df_without_nrc = pd.read_csv(signatures_fn_without_nrc, sep="\t")

# filtered dataframes
orig_emo_df_filtered = orig_emo_df.loc[orig_emo_df['SonnetID'].isin(ids_to_keep)]
orig_highemo_df_filtered = orig_highemo_df.loc[orig_highemo_df['SonnetID'].isin(ids_to_keep)]
orig_emo_df_filtered_without_nrc = \
  orig_emo_df_without_nrc.loc[orig_emo_df_without_nrc['SonnetID'].isin(ids_to_keep)]
orig_highemo_df_filtered_without_nrc = \
  orig_highemo_df_without_nrc.loc[orig_highemo_df_without_nrc['SonnetID'].isin(ids_to_keep)]
signatures_df_filtered = signatures_df.loc[signatures_df['SonnetID'].isin(ids_to_keep)]
signatures_df_filtered_without_nrc = \
  signatures_df_without_nrc.loc[signatures_df_without_nrc['SonnetID'].isin(ids_to_keep)]

# write out
#  all data
orig_emo_df_filtered.to_csv(orig_emo_df_fn.replace(".tsv", "_filt.tsv"),
                            sep="\t", index=False)
orig_highemo_df_filtered.to_csv(orig_highemo_df_fn.replace(".tsv", "_filt.tsv"),
                            sep="\t", index=False)
signatures_df_filtered.to_csv(signatures_fn.replace(".tsv", "_filt.tsv"),
                              sep="\t", index=False)
#  no nrc
orig_emo_df_filtered_without_nrc.to_csv(
  orig_emo_df_fn_without_nrc.replace(".tsv", "_filt.tsv"), sep="\t", index=False)
orig_highemo_df_filtered_without_nrc.to_csv(
  orig_highemo_df_fn_without_nrc.replace(".tsv", "_filt.tsv"), sep="\t", index=False)
signatures_df_filtered_without_nrc.to_csv(signatures_fn_without_nrc.replace(".tsv", "_filt.tsv"),
                                          sep="\t", index=False)

# log to console
deleted_ids = set(orig_emo_df['SonnetID'].tolist()).difference(set(ids_to_keep))
print("# Deleted IDs")
for did in sorted(deleted_ids):
  print(did)