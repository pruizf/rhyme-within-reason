"""Get valence values for call-echo pairs"""

from importlib import reload
import numpy as np
import pandas as pd
from time import strftime
import warnings


import config as cf


if __name__ == "__main__":
  warnings.filterwarnings('ignore')
  print(f"- Start [{strftime('%H:%M:%S')}]")
  cdf = pd.read_csv(cf.df_emos, sep="\t")
  # add signature column for valence
  cdf['sig'] = cdf[['valence_call_b', 'valence_echo_b']].apply(
    lambda row: ''.join(row.values.astype(str)), axis=1)
  # extract just the sonnet id (as unique merging key) and the signatures
  sig_df = cdf[['SonnetID', 'sig']]
  # create count table
  sig_df_counts = sig_df.groupby(['SonnetID', 'sig'])['sig'].aggregate('count')
  sig_df_counts_tcd = sig_df_counts.unstack()
  # merge sonnet metadata with the signatures
  cdf_dedup = cdf.drop_duplicates(subset='SonnetID', keep='first')
  # https://stackoverflow.com/a/42765878/16449778
  mdf = pd.merge(sig_df_counts_tcd,
                 cdf_dedup[['SonnetID', 'AuthorID', 'Author', 'Gender', 'Date']],
                 on='SonnetID', how='inner')
  mdf = mdf[['SonnetID', 'AuthorID', 'Author', 'Gender', 'Date',
             '00', '01', '09', '10', '11', '19', '90', '91', '99']]
  sig_renamer = {k: f"v{k}" for k in ['00', '01', '09', '10', '11', '19', '90', '91', '99']}
  mdf = mdf.rename(columns=sig_renamer)
  mdf.to_csv(cf.df_sig_path, sep='\t', index=False)
