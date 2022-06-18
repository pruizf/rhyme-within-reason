"""Add emotion and polarity information from lexica to corpus rhymes"""

from importlib import reload
from lxml import etree
import numpy as np
import pandas as pd
from time import strftime
import warnings

from sklearn.preprocessing import MinMaxScaler

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
# hash the lexica
# for each word-form
#   add infos to df if found in lexica
#   if not found, see if find infos for their lemma and add
# per-poem info (poems with all rhymes covered vs not)


def collect_emotions_per_term(lx):
  lem2scores = {}
  df = pd.read_csv(lx, sep="\t")
  for idx, row in df.iterrows():
    lem = row['Spanish-es'].lower()
    lem2scores.setdefault(lem, {})
    lem2scores[lem][row["emotion"]] = row["emotion-intensity-score"]
  return lem2scores


def collect_stadthagen_vad(lx):
  lem2scores = {}
  df = pd.read_csv(lx, encoding="latin1")
  mm = MinMaxScaler()
  df[['ValenceMeanScaled']] = mm.fit_transform(df[['ValenceMean']])
  for idx, row in df.iterrows():
    lem = row['Word'].lower()
    lem2scores.setdefault(lem, {})
    lem2scores[lem]["valence"] = row["ValenceMeanScaled"]
  return lem2scores



def collect_vad_per_term(lx):
  """VAD varies according to term sense, collect a median"""
  lem2scores = {}
  lem2aves = {}
  df = pd.read_csv(lx, sep="\t")
  for idx, row in df.iterrows():
    lem = row['Spanish-es'].lower()
    lem2scores.setdefault(lem, {"valence": [], "arousal": [], "dominance": []})
    for attr in ("valence", "arousal", "dominance"):
      lem2scores[lem][attr].append(row[attr[0].upper()+attr[1:]])
  for lem, scores in lem2scores.items():
    lem2aves[lem] = {}
    for attr, scores in scores.items():
      lem2aves[lem][attr] = np.median(np.array(scores))
  return lem2scores, lem2aves


def hash_mlsenticon(fn):
  """
  Hash Senticon lexicon information as a lemma: (pos, polarity) dict.
  Also store part of speech in the dict, and polarity will be a median
  over all PoS. Keys will be in lowercase.
  """
  lem2scores = {}
  lem2aves = {}
  tree = etree.parse(fn)
  terms = tree.xpath("//lemma")
  for term in terms:
    lemma = term.xpath("./text()")[0].strip()
    lem2scores.setdefault(lemma, {"pol": [], "pos": [], "std": []})
    lem2scores[lemma]["pol"].append(float(term.attrib["pol"]))
    lem2scores[lemma]["std"].append(float(term.attrib["std"]))
    lem2scores[lemma]["pos"].append(term.attrib["pos"])
  for lem, scores in lem2scores.items():
    lem2aves[lem] = {}
    for attr, scores in scores.items():
      if attr == "pos":
        lem2aves[lem][attr] = ";".join(lem2scores[lem][attr])
      elif attr == "pol":
        lem2aves[lem]["valence"] = np.median(np.array(scores))
  return lem2scores, lem2aves


def add_annots_to_df(df, idx, annots, target, lextype, mode="lemma"):
  """
  Given a dataframe at index `idx`, add its emotion and VAD
  annotations to the relevant (emotion_call or emotion_echo) column;
  `lextype` shows whether EI or VAD was the source lexicon.
  """
  assert target in ("call", "echo")
  assert lextype in ("vad", "ei", "mls")
  assert mode in ("lemma", "wf", "mls_lemma")
  # keys (ename) are lowercase VAD and emotion names
  for ename, escore in annots.items():
    #bin_score = [0]
    # we don't care about part of speech  now
    if ename == "pos":
      continue
    df.loc[idx, f"{ename}_{target}"] = escore
  modesuf = "wf_" if mode == "wf" else ""
  df.loc[idx, f"{target}_{modesuf}in_{lextype}"] = 1


if __name__ == "__main__":
  warnings.filterwarnings('ignore')
  print(f"- Start [{strftime('%H:%M:%S')}]")
  cdf = pd.read_csv(cf.df_lem_sets, sep="\t")
  # preprocessing
  cdf['Echo'].replace(' ', np.nan, inplace=True)
  # emo and vad df just in case (but infos are hashed into a dict elsewhere)
  edf = pd.read_csv(cf.nrc_ei, sep="\t")
  vdf = pd.read_csv(cf.nrc_vad, sep="\t")
  # Get lexicon data ----------------------------------------------------------
  # hash emos per lemma
  print(f"-   Hash emotions [{strftime('%H:%M:%S')}]")
  lem2emo = collect_emotions_per_term(cf.nrc_ei)
  # hash vad per lemma
  print(f"-   Hash VAD [{strftime('%H:%M:%S')}]")
  #lem2vad_raw, lem2vad = collect_vad_per_term(cf.nrc_vad)
  lem2vad = collect_stadthagen_vad(cf.stadthagen)
  # hash ml-senticon
  print(f"-   Hash ML-Senticon [{strftime('%H:%M:%S')}]")
  lem2mls_raw, lem2mls = hash_mlsenticon(cf.mlsenticon)
  # prepare df columns to keep track of hits
  #    vad, ei
  cdf["call_in_vad"] = np.nan
  cdf["echo_in_vad"] = np.nan
  cdf["call_in_ei"] = np.nan
  cdf["echo_in_ei"] = np.nan
  cdf["call_wf_in_vad"] = np.nan
  cdf["echo_wf_in_vad"] = np.nan
  cdf["call_wf_in_ei"] = np.nan
  #    ml-senticon
  cdf["call_in_mls"] = np.nan
  cdf["echo_in_mls"] = np.nan
  cdf["call_wf_in_mls"] = np.nan
  cdf["echo_wf_in_mls"] = np.nan
  for emoname in cf.emonames:
    cdf[f"{emoname}_call"] = np.nan
    cdf[f"{emoname}_echo"] = np.nan
  for vadname in cf.vadnames:
    cdf[f"{vadname}_call"] = np.nan
    cdf[f"{vadname}_echo"] = np.nan
  print(f"-   Populate df [{strftime('%H:%M:%S')}]")
  for idx, row in cdf.iterrows():
    # get emo and vad for row
    einfos_call = lem2emo.get(row.CallLemma.lower())
    einfos_echo = lem2emo.get(row.EchoLemma.lower())
    vinfos_call = lem2vad.get(row.CallLemma.lower())
    vinfos_echo = lem2vad.get(row.EchoLemma.lower())
    #vinfos_call_raw = lem2vad_raw.get(row.CallLemma.lower())
    #vinfos_echo_raw = lem2vad_raw.get(row.EchoLemma.lower())
    # TODO function for below that takes row and works on call or echo
    # TODO based on "call" "echo" argument
    # populate emo and vad columns --------------------------------------------
    #   call ei
    if einfos_call is not None:
      add_annots_to_df(cdf, idx, einfos_call, "call", "ei")
    else:
      einfos_call_wf = lem2emo.get(row.Call.lower())
      if einfos_call_wf is not None:
        add_annots_to_df(cdf, idx, einfos_call_wf, "call", "ei", mode="wf")
    #   echo ei
    if einfos_echo is not None:
      add_annots_to_df(cdf, idx, einfos_echo, "echo", "ei")
    else:
      row_echo = row.Echo.lower() if pd.notna(row.Echo) else row.Echo
      einfos_echo_wf = lem2emo.get(row_echo)
      if einfos_echo_wf is not None:
        add_annots_to_df(cdf, idx, einfos_echo_wf, "echo", "ei", mode="wf")
    #   call vad
    if vinfos_call is not None:
      add_annots_to_df(cdf, idx, vinfos_call, "call", "vad")
    else:
      vinfos_call_wf = lem2vad.get(row.Call.lower())
      if vinfos_call_wf is not None:
        add_annots_to_df(cdf, idx, vinfos_call_wf, "call", "vad", mode="wf")
      # try mlsenticon if nrc no results
      else:
        minfos_call = lem2mls.get(row.CallLemma.lower())
        if minfos_call is not None:
          add_annots_to_df(cdf, idx, minfos_call, "call", "mls")
        else:
          minfos_call_wf = lem2mls.get(row.Call.lower())
          if minfos_call is not None:
            add_annots_to_df(cdf, idx, minfos_call, "call", "mls", mode="wf")

    #   echo vad
    if vinfos_echo is not None:
      add_annots_to_df(cdf, idx, vinfos_echo, "echo", "vad")
    else:
      row_echo = row.Echo.lower() if pd.notna(row.Echo) else row.Echo
      vinfos_echo_wf = lem2vad.get(row_echo)
      if vinfos_echo_wf is not None:
        add_annots_to_df(cdf, idx, vinfos_echo_wf, "echo", "vad", mode="wf")
      # try mlsenticon if nrc no results
      else:
        minfos_echo = lem2mls.get(row.EchoLemma.lower())
        if minfos_echo is not None:
          add_annots_to_df(cdf, idx, minfos_echo, "echo", "mls")
        else:
          minfos_call_wf = lem2mls.get(row.Echo.lower()) if pd.notna(row.Echo) else row.Echo
          if minfos_echo is not None:
            add_annots_to_df(cdf, idx, minfos_echo, "echo", "mls", mode="wf")

    if idx > 0 and not idx % 5000:
      print(f"    - Done {idx} rhymes [{strftime('%H:%M:%S')}]")

  cdf.to_csv(cf.df_emos, sep='\t', index=False)
  print(f"- End [{strftime('%H:%M:%S')}]\n")

  # print
  pd.options.display.float_format = "{:,.2f}".format
  percent_missing = cdf.isnull().sum() * 100 / len(cdf)
  percent_available = 100 - percent_missing
  missing_value_df = pd.DataFrame({'column_name': cdf.columns,
                                   'percent_available': percent_available,
                                   'percent_missing': percent_missing})
  print(missing_value_df)

