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


# Word-forms with clitics not all caught by the `strip_affixes()` function above
custom_lemmas = {"desvelo": "desvelar",
                 "acometellas": "acometer",
                 "alcanzallas": "alcanzar",
                 "bastalle": "vencer",
                 "cantimploras": "cantimplora",
                 "cegalle": "cegar",
                 "conocellas": "conocer",
                 "contalle": "contar",
                 "descomponellos": "descomponer",
                 "egehe(n)la": "egeheno",
                 "entendellas": "entender",
                 "escribillos": "escribir",
                 "esp(e)çial": "especial",
                 "estandartes": "estandarte",
                 "formalle": "formar",
                 "frondoso": "frondoso",
                 "ladralle": "ladrar",
                 "levantose": "levantar",
                 "longino": "vero-longino",
                 "maldecillo": "maldecir",
                 "matalle": "matar",
                 "mayordomo": "mayordomo",
                 "meterla": "meter",
                 "mostralle": "mostrar",
                 "padecelle": "padecer",
                 "padecellos": "padecer",
                 "parla": "parla",
                 "perla": "perla",
                 "pasarla": "pasar",
                 "perdellas": "perder",
                 "perseguirme": "perseguir",
                 "preguntole": "preguntar",
                 "premialle": "premiar",
                 "rebelallos": "rebelar",
                 "regalallos": "regalar",
                 "sacerdote": "sacerdote",
                 "satisfacelle": "satisfacer",
                 "sentillos": "sentir",
                 "tabardillo": "tabardillo",
                 "temellas": "temer",
                 "temellos": "temer",
                 "tenellas": "tender",
                 "tenellos": "tener",
                 "tomalle": "tomar",
                 "vencelle": "vencer",
                 "vencello": "vencer",
                 "vencellos": "vencer",
                 "vendellos": "vender",
                 "vero": "vero-longino",
                 "vero-longino": "vero-longino",
                 "çial": "especial",
                 "probarla": "probar",
                 "verterla": "verter",
                 "merla": "merlar",
                 "pagarla": "pagar",
                 "verla": "ver",
                 "borla": "borla",
                 "turba": "turba",
                 "orla": "orla",
                 "burla": "burla"
                 }

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
  if False:
    call_word_lemmas = []
    echo_word_lemmas = []
    echo_set_lemmas = []
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
    if False:
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
    if False:
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
    #logfd.flush()

    # if pidx > 0 and not pidx % 100:
    #   print(f"- Done echos {pidx} poems [{strftime('%R')}]")
    # if pidx > 10000:
    #   break

  if False:
    assert len(call_word_lemmas) == len(df)
    assert len(echo_word_lemmas) == len(df)
    df['CallLemma'] = call_word_lemmas
    df['EchoLemma'] = echo_word_lemmas

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

  df.to_csv(cf.df_lem, sep='\t', index=False)

  logfd.close()
