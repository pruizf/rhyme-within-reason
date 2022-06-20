"""
Add emotion and polarity information from lexica to corpus rhymes
"""

from importlib import reload
from lxml import etree
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
from time import strftime
import warnings

from sklearn.preprocessing import MinMaxScaler

import config as cf

DBG = False


def collect_nrc_emotions_per_term(lx):
  """
  Collect emotions from NRC emotion intensity Spanish lexicon.
  Note: NRC scores are already scaled.
  """
  lem2scores = {}
  df = pd.read_csv(lx, sep="\t")
  for idx, row in df.iterrows():
    lem = row['Spanish-es'].lower()
    lem2scores.setdefault(lem, {})
    lem2scores[lem][row["emotion"]] = row["emotion-intensity-score"]
  return lem2scores


def collect_emotions_stadthagen_per_term(lx):
  """Collect emotions from Stadthagen et al. 2018 lexicon"""
  lem2scores = {}
  df = pd.read_csv(lx, encoding="latin1")
  df = df.rename(columns=cf.stadthagen_emos_renamer)
  # scale data
  for colname in cf.emonames:
    try:
      coldata = df[[colname]]
    except KeyError:
      continue
    mm = MinMaxScaler()
    df[colname] = mm.fit_transform(coldata)
  for idx, row in df.iterrows():
    lem = row['Word'].lower()
    lem2scores.setdefault(lem, {})
    for emoname in cf.emonames:
      try:
        lem2scores[lem][emoname] = row[emoname]
      except KeyError:
        continue
  return lem2scores


def collect_va_stadthagen(lx):
  """
  Collect Valence and Arousal scores from Stadthagen 2018
  MinMax scale for compatibility with other datasets
  """
  lem2scores = {}
  df = pd.read_csv(lx, encoding="latin1")
  mm = MinMaxScaler()
  df[['ValenceMeanScaled']] = mm.fit_transform(df[['ValenceMean']])
  df[['ArousalMeanScaled']] = mm.fit_transform(df[['ArousalMean']])
  for idx, row in df.iterrows():
    lem = row['Word'].lower()
    lem2scores.setdefault(lem, {})
    lem2scores[lem]["valence"] = row["ValenceMeanScaled"]
    lem2scores[lem]["arousal"] = row["ArousalMeanScaled"]
  return lem2scores


def collect_nrc_vad_per_term(lx):
  """
  Get VAD from NRC Spanish file.
  VAD varies according to term sense, collect a median.
  Note: NRC scores are already scaled.
  """
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
  # scale medians
  all_valence_scores = np.array([it["valence"] for it in lem2aves.values()])
  mm = MinMaxScaler()
  # reshape for single feature
  all_valence_scaled = mm.fit_transform(all_valence_scores.reshape(-1,1))
  all_valence_scaled.flatten()
  score_zip = zip(all_valence_scores, all_valence_scaled)
  score_dict = {raw : scaled for raw, scaled in score_zip}
  for lem, scores in lem2scores.items():
    for attr, scores in scores.items():
      if attr == "pol":
        lem2aves[lem]["valence"] = score_dict[lem2aves[lem]["valence"]]
  return lem2scores, lem2aves


def add_annots_to_df(df, idx, annots, target, lextype, mode="lemma"):
  """
  Given a dataframe at index `idx`, add its emotion and VAD
  annotations to the relevant (emotion_call or emotion_echo) column;
  `lextype` shows whether EI or VAD was the source lexicon.
  """
  assert target in ("call", "echo")
  assert lextype in ("vad", "ei", "nvad", "nei", "mls")
  assert mode in ("lemma", "wf", "mls_lemma")
  # keys (ename) are lowercase VAD and emotion names
  for ename, escore in annots.items():
    # we don't care about part of speech  now
    if ename == "pos":
      continue
    df.loc[idx, f"{ename}_{target}"] = escore
  modesuf = "wf_" if mode == "wf" else ""
  df.loc[idx, f"{target}_{modesuf}in_{lextype}"] = 1


def binarize_scores(sco):
  """
  Used to render (valence) scores as binary.
  0 will be negative valence, 1 will be positive.
  Null values recoded as -9.
  """
  if pd.isna(sco):
    bsco = 9
  else:
    bsco = 0 if sco < 0.5 else 1
  return bsco


if __name__ == "__main__":
  warnings.filterwarnings('ignore')
  print(f"- Start [{strftime('%H:%M:%S')}]")
  print(f"- Output file is [{cf.df_emos}]")
  print(f"- Coverage written to [{cf.df_coverage_path}]")
  cdf = pd.read_csv(cf.df_lem_sets, sep="\t")
  # preprocessing
  cdf['Echo'].replace(' ', np.nan, inplace=True)
  # nrc emo and vad df just in case (but infos are hashed into a dict elsewhere)
  edf = pd.read_csv(cf.nrc_ei, sep="\t")
  vdf = pd.read_csv(cf.nrc_vad, sep="\t")
  # Get lexicon data ----------------------------------------------------------
  # hash emos per lemma
  print(f"-   Hash Stadthagen Emos [{strftime('%H:%M:%S')}]")
  lem2emo = collect_emotions_stadthagen_per_term(cf.stadthagen_emos)
  print(f"-   Hash NRC EI [{strftime('%H:%M:%S')}]")
  lem2nei = collect_nrc_emotions_per_term(cf.nrc_ei)
  lem2nvad_raw, lem2nvad = collect_nrc_vad_per_term(cf.nrc_vad)
  print(f"-   Hash NRC VAD [{strftime('%H:%M:%S')}]")
  lem2vad = collect_va_stadthagen(cf.stadthagen)
  # hash vad per lemma
  print(f"-   Hash Stadthagen VA [{strftime('%H:%M:%S')}]")
  # hash ml-senticon
  print(f"-   Hash ML-Senticon [{strftime('%H:%M:%S')}]")
  lem2mls_raw, lem2mls = hash_mlsenticon(cf.mlsenticon)
  # prepare df columns to keep track of hits ----------------------------------
  # several flag columns to help filter by source, actual scores added elsewhere
  #    vad, ei (Stadthagen)
  cdf["call_in_vad"] = np.nan
  cdf["echo_in_vad"] = np.nan
  cdf["call_in_ei"] = np.nan
  cdf["echo_in_ei"] = np.nan
  cdf["call_wf_in_vad"] = np.nan
  cdf["echo_wf_in_vad"] = np.nan
  cdf["call_wf_in_ei"] = np.nan
  cdf["echo_wf_in_ei"] = np.nan
  #    vad, ei (NRC)
  cdf["call_in_nvad"] = np.nan
  cdf["echo_in_nvad"] = np.nan
  cdf["call_in_nei"] = np.nan
  cdf["echo_in_nei"] = np.nan
  cdf["call_wf_in_nvad"] = np.nan
  cdf["echo_wf_in_nvad"] = np.nan
  cdf["call_wf_in_nei"] = np.nan
  cdf["echo_wf_in_nei"] = np.nan
  #    ml-senticon
  cdf["call_in_mls"] = np.nan
  cdf["echo_in_mls"] = np.nan
  cdf["call_wf_in_mls"] = np.nan
  cdf["echo_wf_in_mls"] = np.nan
  # colums for actual scores --------------------------------------------------
  for emoname in cf.emonames:
    cdf[f"{emoname}_call"] = np.nan
    cdf[f"{emoname}_echo"] = np.nan
  for vadname in cf.vadnames:
    cdf[f"{vadname}_call"] = np.nan
    cdf[f"{vadname}_echo"] = np.nan
  print(f"-   Populate df [{strftime('%H:%M:%S')}]")
  # Populate emo and vad columns --------------------------------------------
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

    #   call ei (Stadthagen) ------------------------------
    if einfos_call is not None:
      add_annots_to_df(cdf, idx, einfos_call, "call", "ei")
    else:
      einfos_call_wf = lem2emo.get(row.Call.lower())
      if einfos_call_wf is not None:
        add_annots_to_df(cdf, idx, einfos_call_wf, "call", "ei", mode="wf")
      # try NRC if Stadthagen no result
      else:
        ninfos_call = lem2nei.get(row.CallLemma.lower())
        if ninfos_call is not None:
          add_annots_to_df(cdf, idx, ninfos_call, "call", "nei")
        else:
          ninfos_call_wf = lem2nei.get(row.Call.lower())
          if ninfos_call_wf is not None:
            add_annots_to_df(cdf, idx, ninfos_call_wf, "call", "nei", mode="wf")
    #   echo ei (Stadthagen) ------------------------------
    if einfos_echo is not None:
      add_annots_to_df(cdf, idx, einfos_echo, "echo", "ei")
    else:
      row_echo = row.Echo.lower() if pd.notna(row.Echo) else row.Echo
      einfos_echo_wf = lem2emo.get(row_echo)
      if einfos_echo_wf is not None:
        add_annots_to_df(cdf, idx, einfos_echo_wf, "echo", "ei", mode="wf")
      # try NRC if Stadthagen no result
      else:
        ninfos_echo = lem2nei.get(row.EchoLemma.lower())
        if ninfos_echo is not None:
          add_annots_to_df(cdf, idx, ninfos_echo, "echo", "nei")
        else:
          ninfos_echo_wf = lem2nei.get(row_echo)
          if ninfos_echo_wf is not None:
            add_annots_to_df(cdf, idx, ninfos_echo_wf, "echo", "nei", mode="wf")
    #   call vad (Stadthagen) -----------------------------
    if vinfos_call is not None:
      add_annots_to_df(cdf, idx, vinfos_call, "call", "vad")
    else:
      vinfos_call_wf = lem2vad.get(row.Call.lower())
      if vinfos_call_wf is not None:
        add_annots_to_df(cdf, idx, vinfos_call_wf, "call", "vad", mode="wf")
      # try NRC if Stadthagen no result
      else:
        nvinfos_call = lem2nvad.get(row.CallLemma.lower())
        if nvinfos_call is not None:
          add_annots_to_df(cdf, idx, nvinfos_call, "call", "nvad")
        else:
          nvinfos_call_wf = lem2nvad.get(row.Call.lower())
          if nvinfos_call_wf is not None:
            add_annots_to_df(cdf, idx, nvinfos_call_wf, "call", "nvad", mode="wf")
          # try mlsenticon if Stadthagen and NRC no results
          else:
            minfos_call = lem2mls.get(row.CallLemma.lower())
            if minfos_call is not None:
              add_annots_to_df(cdf, idx, minfos_call, "call", "mls")
            else:
              minfos_call_wf = lem2mls.get(row.Call.lower())
              if minfos_call_wf is not None:
                add_annots_to_df(cdf, idx, minfos_call_wf, "call", "mls", mode="wf")

    #   echo vad  (Stadthagen) ----------------------------
    if vinfos_echo is not None:
      add_annots_to_df(cdf, idx, vinfos_echo, "echo", "vad")
    else:
      row_echo = row.Echo.lower() if pd.notna(row.Echo) else row.Echo
      vinfos_echo_wf = lem2vad.get(row_echo)
      if vinfos_echo_wf is not None:
        add_annots_to_df(cdf, idx, vinfos_echo_wf, "echo", "vad", mode="wf")
      # try NRC if Stadthagen no result
      else:
        nvinfos_echo = lem2nvad.get(row.EchoLemma.lower())
        if nvinfos_echo is not None:
          add_annots_to_df(cdf, idx, nvinfos_echo, "echo", "nvad")
        else:
          nvinfos_echo_wf = lem2nvad.get(row_echo)
          if nvinfos_echo_wf is not None:
            add_annots_to_df(cdf, idx, nvinfos_echo_wf, "echo", "nvad", mode="wf")
          # try mlsenticon if Stadthagen and NRC no results
          else:
            minfos_echo = lem2mls.get(row.EchoLemma.lower())
            if minfos_echo is not None:
              add_annots_to_df(cdf, idx, minfos_echo, "echo", "mls")
            else:
              minfos_echo_wf = lem2mls.get(row_echo)
              if minfos_echo_wf is not None:
                add_annots_to_df(cdf, idx, minfos_echo_wf, "echo", "mls", mode="wf")

    if idx > 0 and not idx % 5000:
      print(f"    - Done {idx} rhymes [{strftime('%H:%M:%S')}]")

  # add binary features
  for infix in ('call', 'echo'):
    cdf[f'valence_{infix}_b'] = cdf[f'valence_{infix}'].apply(binarize_scores)
    cdf[f'valence_{infix}_b'] = cdf[f'valence_{infix}_b'].astype(
      CategoricalDtype([0, 1, 9]))

  cdf.to_csv(cf.df_emos, sep='\t', index=False)
  print(f"- End [{strftime('%H:%M:%S')}]\n")

  # print summary
  pd.options.display.float_format = "{:,.2f}".format
  pd.set_option('display.max_rows', 70)
  percent_missing = cdf.isnull().sum() * 100 / len(cdf)
  percent_available = 100 - percent_missing
  missing_value_df = pd.DataFrame({'column_name': cdf.columns,
                                   'percent_available': percent_available,
                                   'percent_missing': percent_missing})
  print(missing_value_df)
  missing_value_df.to_csv(cf.df_coverage_path, sep="\t", index=False)
