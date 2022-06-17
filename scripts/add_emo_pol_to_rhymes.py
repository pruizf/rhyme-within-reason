"""Add emotion and polarity information from lexica to corpus rhymes"""

from importlib import reload
import pandas as pd
import numpy as np

from time import strftime

import warnings
warnings.filterwarnings('ignore')


DBG = False


import config as cf

# nrc emotion intensity structure
"""" (tab sep)
word	Spanish-es	emotion	emotion-intensity-score
outraged	indignado	anger	0.964
brutality	brutalidad	anger	0.959
...
brutality	brutalidad	fear	0.922
"""

# TODO
# add vad columns
# add columns for emotion intensity
# iterate over corpus df
#   for each lemma
#     iterate over vad and EI to collect infos
#     add them to the df


def collect_emotions_per_term(lx):
  lem2scores = {}
  df = pd.read_csv(lx, sep="\t")
  for idx, row in df.iterrows():
    lem = row['Spanish-es']
    lem2scores.setdefault(lem, {})
    lem2scores[lem][row["emotion"]] = row["emotion-intensity-score"]
  return lem2scores


def collect_vad_per_term(lx):
  """VAD varies according to term sense, collect an average"""
  lem2scores = {}
  lem2aves = {}
  df = pd.read_csv(lx, sep="\t")
  for idx, row in df.iterrows():
    lem = row['Spanish-es']
    lem2scores.setdefault(lem, {"valence": [], "arousal": [], "dominance": []})
    for attr in ("valence", "arousal", "dominance"):
      lem2scores[lem][attr].append(row[attr[0].upper()+attr[1:]])
  for lem, scores in lem2scores.items():
    lem2aves[lem] = {}
    for attr, scores in scores.items():
      lem2aves[lem][attr] = np.average(np.array(scores))
  return lem2scores, lem2aves


def add_annots_to_df(df, idx, annots, target):
  assert target in ("call", "echo")
  for ename, escore in annots.items():
    df.loc[idx, f"{ename}_{target}"] = escore


if __name__ == "__main__":
  print(f"- Start [{strftime('%R')}]")
  cdf = pd.read_csv(cf.df_lem_sets, sep="\t")
  # emo and vad df just in case (but infos are hashed into a dict elsewhere)
  edf = pd.read_csv(cf.nrc_ei, sep="\t")
  vdf = pd.read_csv(cf.nrc_vad, sep="\t")
  # hash emos per lemma
  print(f"-   Hash emotions [{strftime('%R')}]")
  lem2emo = collect_emotions_per_term(cf.nrc_ei)
  # hash vad per lemma
  print(f"-   Hash VAD [{strftime('%R')}]")
  lem2vad_raw, lem2vad = collect_vad_per_term(cf.nrc_vad)
  for emoname in cf.emonames:
    cdf[f"{emoname}_call"] = np.nan
    cdf[f"{emoname}_echo"] = np.nan
  for vadname in cf.vadnames:
    cdf[f"{vadname}_call"] = np.nan
    cdf[f"{vadname}_echo"] = np.nan
  #TODO: actually, should look at the word-form too if lemma not found in lexica
  for idx, row in cdf.iterrows():
    call_lemma = row.CallLemma
    echo_lemma = row.EchoLemma
    #if lemma == "gloria":
    #  breakpoint()
    einfos_call = lem2emo.get(call_lemma)
    einfos_echo = lem2emo.get(echo_lemma)
    vinfos_call = lem2vad.get(call_lemma)
    vinfos_echo = lem2vad.get(echo_lemma)
    vinfos_call_raw = lem2vad_raw.get(call_lemma)
    vinfos_echo_raw = lem2vad_raw.get(echo_lemma)
    # if einfos_call is not None:
    #   for ename, escore in einfos_call.items():
    #     cdf.loc[idx, f"{ename}_call"] = escore
    # if einfos_echo is not None:
    #   for ename, escore in einfos_echo.items():
    #     cdf.loc[idx, f"{ename}_echo"] = escore
    if einfos_call is not None:
      add_annots_to_df(cdf, idx, einfos_call, "call")
    if einfos_echo is not None:
      add_annots_to_df(cdf, idx, einfos_echo, "echo")
    if vinfos_call is not None:
      add_annots_to_df(cdf, idx, vinfos_call, "call")
    if vinfos_echo is not None:
      add_annots_to_df(cdf, idx, vinfos_echo, "echo")
  cdf.to_csv(cf.df_emos, sep='\t', index=False)
  print(f"- End [{strftime('%R')}]")
