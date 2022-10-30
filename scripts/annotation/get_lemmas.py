"""
Get lemmas (in context) for rhyme words using Stanza.
"""

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

from custom_lemmas import custom_lemmas

warnings.filterwarnings('ignore')


DBG = False

puncts = ".,;:!?«»"

def clean_token(tk):
  #TODO remov these cases
  if tk == "descubrilla":
    return "descubrirla"
  elif tk == "decillo":
    return "decirlo"
  elif tk == "sentillo":
    return "sentirlo"
  elif tk == "sentillos":
    return "sentirlos"
  tk = re.sub("-$", "", tk)
  tk = tk.replace("?", "")
  tk = tk.replace("…", "")
  tk = re.sub(r"[{}]+$".format(puncts), "", tk)
  tk = re.sub(r"'$", "", tk)
  return tk


def strip_affixes(tk):
  """Strip clitics off"""
  #TODO remove these cases
  if tk == "decillos":
    return "decir"
  tk = re.sub(r"^(vert|alleg|.*?r|.*?)([aeiáéí][rd])(?:[mts]e|l[oea]s?|[nv]?os?)+", r"\1\2", tk)
  return tk


def clean_line(line):
  """Pre-treat line for better tokenization"""
  line_orig = line
  line = re.sub(r"-[\s{}]?$".format(puncts), "", line)
  line = re.sub(r"^-[\s]?", "- ", line)
  line = re.sub(r"(\w)-(\s)", r"\1 - \2", line)
  line = re.sub(r"(\s)-(\w)", r"\1 - \2", line)
  line = line.replace("descubrilla", "descubrirla")
  line = line.replace("decillo", "decirlo")
  line = line.replace("decillos", "decirlos")
  line = line.replace("sentillo", "sentirlo")
  line = line.replace("sentillos", "sentirlos")
  if line_orig != line:
    print("  - Line rep:", line_orig, line)
  return line


def add_lemmas_to_df(part_df, whole_df, column, word_forms):
  words_for_lemmas = part_df[column].str.lower().tolist()
  last_index = 0
  for call_word in call_words:
    clean_call_word = clean_token(call_word)
    if clean_call_word in custom_lemmas:
      call_lemma = custom_lemmas[clean_call_word]
    elif "(" in call_word or ")" in clean_call_word:
      call_lemma = "UNK"
      print(f"  - Call: [{call_word}] Lemma: [UNK]")
    else:
      call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == clean_call_word]
      if len(call_word_infos) == 0:
        call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == strip_affixes(clean_call_word)]
      assert len(call_word_infos) > 0


skip_call_words = {"esp", "e"}
skip_echo_words = {"esp", "e"}

# in case need to examine lemmas
logfd = open("../data/lemma_log.txt", mode="w")

if __name__ == "__main__":
  print(f"- Start [{strftime('%R')}]")
  #nlp = spacy.load(cf.spacy_model)
  nlp = spacy_stanza.load_pipeline("es", processors="tokenize,pos,lemma",
                                   verbose=False, logging_level='ERROR')
  df = pd.read_csv(cf.df_path, sep="\t", index_col=None)

  df.replace("", np.nan, inplace=True)
  df = df.dropna(axis=0, how='all')

  poem_ids = df['SonnetID'].unique()
  # nan not equal to itself
  poem_ids = list(filter(lambda pid: pid==pid, poem_ids))
  call_word_lemmas = []
  echo_word_lemmas = []
  # main loop =================================================================
  for pidx, poem_id in enumerate(poem_ids):
    if pidx < 0:
      continue
    poem_infos = df.loc[df['SonnetID'] == poem_id]
    # get poem text
    raw_txt = poem_infos['Text'].iloc[0]
    all_lines = []
    all_rhyme_words = []
    all_rhyme_contexts = []
    stanzas = re.split(r"#+", raw_txt)
    for stz in stanzas:
      lines = [clean_line(l.strip()) for l in re.split(r"~+", stz)]
      all_lines.extend(lines)
    # analyze poem with complete text (for context before and after rhyme)
    wf_infos = []
    clean_txt = "\n".join(all_lines)
    poem_ana = nlp(clean_txt)
    for toko in poem_ana:
      wf_infos.append([toko.text.lower(), toko.lemma_.lower(), toko.idx])
    # get lemmas for call words ---------------------------
    call_words = poem_infos['Call'].str.lower().tolist()
    last_call_index = 0
    for call_word in call_words:
      clean_call_word = clean_token(call_word)
      if clean_call_word in skip_call_words:
        print(f"  - Skipping call word: [{clean_call_word}]")
        call_word_lemmas.append("BADWF")
        continue
      if clean_call_word in custom_lemmas:
        call_lemma = [custom_lemmas[clean_call_word]]
        call_word_infos = [['', '', last_call_index]]
      elif "(" in call_word or ")" in clean_call_word:
        call_lemma = ["UNK"]
        call_word_infos = [['', '', last_call_index]]
        print(f"  - Call: [{call_word}] Lemma: [UNK]")
      else:
        call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == clean_call_word]
        if len(call_word_infos) == 0:
          call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == strip_affixes(clean_call_word)]
        assert len(call_word_infos) > 0
        # get the lemma for the first possible word-form after the last one covered
        call_lemma = [cw[1] for cw in call_word_infos if cw[-1] >= last_call_index]
        assert len(call_lemma) > 0
      last_call_index = min([cw[-1] for cw in call_word_infos if cw[-1] >= last_call_index])
      DBG and logfd.write("{}\t{}\n".format(call_word, call_lemma[0]))
      #print("  - {} {}".format(call_word, call_lemma[0]))
      call_word_lemmas.append(call_lemma[0])
    logfd.flush()

    if pidx > 0 and not pidx % 100:
      print(f"- Done calls {pidx} poems [{strftime('%R')}]")
    if pidx > 10000:
      break

    # get lemmas for echo ---------------------------------
    echo_words = poem_infos['Echo'].str.lower().tolist()
    last_echo_index = 0
    for echo_word in echo_words:
      if echo_word == ' ':
        echo_word_lemmas.append(" ")
        echo_word_infos = [['', '', last_echo_index]]
        continue
      clean_echo_word = clean_token(echo_word)
      if clean_echo_word in skip_echo_words:
        print(f"  - Skipping echo word: [{clean_echo_word}]")
        echo_word_lemmas.append("BADWF")
        echo_word_infos = [['', '', last_echo_index]]
        continue
      if clean_echo_word in custom_lemmas:
        echo_lemma = [custom_lemmas[clean_echo_word]]
        echo_word_infos = [['', '', last_echo_index]]
      elif "(" in echo_word or ")" in clean_echo_word:
        echo_lemma = ["UNK"]
        echo_word_infos = [['', '', last_echo_index]]
        print(f"  - Call: [{echo_word}] Lemma: [UNK]")
      else:
        echo_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == clean_echo_word]
        if len(echo_word_infos) == 0:
          echo_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == strip_affixes(clean_echo_word)]
        assert len(echo_word_infos) > 0
        #echo_lemma = [cw[1] for cw in echo_word_infos if cw[-1] >= last_echo_index]
        echo_lemma = [cw[1] for cw in echo_word_infos if cw[-1]]
        assert len(echo_lemma) > 0
      #last_echo_index = min([cw[-1] for cw in echo_word_infos if cw[-1] >= last_echo_index])
      last_echo_index = last_echo_index
      DBG and logfd.write("{}\t{}\n".format(echo_word, echo_lemma[0]))
      #print("  - {} {}".format(echo_word, echo_lemma[0]))
      echo_word_lemmas.append(echo_lemma[0])
    # logfd.flush()

    if pidx > 0 and not pidx % 100:
      print(f"- Done echos {pidx} poems [{strftime('%R')}]")
    if pidx > 10000:
      break

  assert len(call_word_lemmas) == len(df)
  assert len(echo_word_lemmas) == len(df)
  df['CallLemma'] = call_word_lemmas
  df['EchoLemma'] = echo_word_lemmas

  df.to_csv(cf.df_lem, sep='\t', index=False)

  logfd.close()
