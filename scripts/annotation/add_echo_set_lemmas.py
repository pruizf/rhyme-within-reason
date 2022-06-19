"""Once the df has lemmas for calls and echos, add lemmas for
echo sets based on the call lemmas"""

#coding=utf8

from importlib import reload
import config as cf
import numpy as np
import pandas as pd
import re
import spacy
import stanza
import spacy_stanza
#from spacy_stanza import StanzaLanguage
from time import strftime

import warnings
warnings.filterwarnings('ignore')


DBG = False

if __name__ == "__main__":
  print(f"- Start [{strftime('%R')}]")
  #nlp = spacy.load(cf.spacy_model)
  nlp = spacy_stanza.load_pipeline("es", processors="tokenize,pos,lemma",
                                   verbose=False, logging_level='ERROR')
  df = pd.read_csv(cf.df_lem, sep="\t", index_col=None)

  df.replace("", np.nan, inplace=True)
  df = df.dropna(axis=0, how='all')

  poem_ids = df['SonnetID'].unique()
  # nan not equal to itself
  poem_ids = list(filter(lambda pid: pid==pid, poem_ids))

  # add set lemmas based on Call lemmas
  echo_set_lemmas = []
  for pidx, poem_id in enumerate(poem_ids):
    if pidx < 0:
      continue
    poem_infos = df.loc[df['SonnetID'] == poem_id]
    # get lemmas for echo chain for each call based on Call + CallLemma columns
    for sidx, row in poem_infos.iterrows():
      row_echo_set_lemmas = []
      echo_set = row['Set']
      if pd.isna(echo_set):
        echo_set_lemmas.append("")
        continue
      echos = [e.strip() for e in echo_set.split(",")]
      for echo2 in echos:
        echo2_lemma = poem_infos.loc[poem_infos['Call'] == echo2, 'CallLemma'].iloc[0]
        row_echo_set_lemmas.append(echo2_lemma)
      echo_set_lemmas.append(", ".join(row_echo_set_lemmas))
    if pidx > 0 and not pidx % 100:
      print(f"- Done echo-sets {pidx} poems [{strftime('%R')}]")
    if pidx > 10000:
      break

  assert len(echo_set_lemmas) == len(df)
  df['SetLemma'] = echo_set_lemmas

  df.to_csv(cf.df_lem_sets, sep='\t', index=False)

