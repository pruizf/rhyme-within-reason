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

#TODO
# read df
# read and split text into lines
# find call and echo as the last word of each line
# get lemmas for each
# write the lemmas to the dataframe
# write df out

DBG = True

puncts = ".,;:!?«»"

def clean_token(tk):
  if tk == "descubrilla":
    return "descubrirla"
  elif tk == "decillo":
    return "decirlo"
  elif tk == "sentillo":
    return "sentirlo"
  tk = re.sub("-$", "", tk)
  tk = tk.replace("?", "")
  tk = tk.replace("…", "")
  tk = re.sub(r"[{}]+$".format(puncts), "", tk)
  tk = re.sub(r"'$", "", tk)
  return tk


def strip_affixes(tk):
  if tk == "decillos":
    return "decir"
  tk = re.sub(r"^(vert|alleg|.*?r|.*?)([aeiáéí][rd])(?:[mts]e|l[oea]s?|[nv]?os?)+", r"\1\2", tk)
  return tk


def custom_replacements(tk):
  tk = re.sub("^desve$", "desvelo", tk)
  return tk


def clean_line(line):
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


custom_lemmas = {"desvelo": "desvelar",
                 "estandartes": "estandarte",
                 "egehe(n)la": "egeheno",
                 "esp(e)çial": "especial",
                 "mayordomo": "mayordomo",
                 "frondoso": "frondoso",
                 "perseguirme": "perseguir",
                 "vero-longino": "vero-longino",
                 "vero": "vero-longino",
                 "longino": "vero-longino",
                 "çial": "especial",
                 "maldecillo": "maldecir",
                 "levantose": "levantar",
                 "sacerdote": "sacerdote",
                 "tabardillo": "tabardillo",
                 "preguntole": "preguntar"}

skip_call_words = {"esp", "e"}

logfd = open("../data/lemma_log.txt", mode="w")

if __name__ == "__main__":
  print(f"- Start [{strftime('%R')}]")
  #snlp = stanza.Pipeline(lang="es", processors="tokenize,pos")
  #nlp = spacy.load(cf.spacy_model)
  #nlp = StanzaLanguage(snlp)
  nlp = spacy_stanza.load_pipeline("es", processors="tokenize,pos,lemma",
                                   verbose=False, logging_level='ERROR')
  df = pd.read_csv(cf.df_path, sep="\t", index_col=None)
  poem_ids = df['SonnetID'].unique()
  # nan not equal to itself
  poem_ids = list(filter(lambda pid: pid==pid, poem_ids))
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
    # store rhyme word-forms
    for stz in stanzas:
      lines = [clean_line(l.strip()) for l in re.split(r"~+", stz)]
      all_lines.extend(lines)

    # line_anas = [nlp(l) for l in all_lines]
    # line_words = [[tok.text for tok in ana if not tok.is_punct and not tok.is_space]
    #               for ana in line_anas]
    # rhyme_words = [clean_token(line[-1]).lower() for line in line_words]
    # all_rhyme_words.extend(rhyme_words)
    # all_rhyme_contexts = {}
    # for idx, line_for_context in enumerate(line_words):
    #   if idx == len(line_words) - 1:
    #     all_rhyme_contexts[(line_for_context[-2], None)] = line_for_context[-1]
    #   # elif line_for_context[-1] in ("me", "te", "se", "nos", "os", "vos", "le",
    #   #                               "lo", "les", "los", "la", "las"):
    #   #
    #   else:
    #     all_rhyme_contexts[(line_for_context[-2], line_words[idx+1][0])] = line_for_context[-1]

    # reanalyze poem with complete text (for context before and after rhyme)
    wf_infos = []
    clean_txt = "\n".join(all_lines)
    poem_ana = nlp(clean_txt)
    for toko in poem_ana:
      wf_infos.append([toko.text.lower(), toko.lemma_.lower(), toko.idx])
    call_words = poem_infos['Call'].str.lower().tolist()
    last_call_index = 0
    for call_word in call_words:
      clean_call_word = clean_token(call_word)
      if clean_call_word in skip_call_words:
        continue
      if clean_call_word in custom_lemmas:
        call_lemma = [custom_lemmas[clean_call_word]]
        call_word_infos = [['', '', last_call_index]]
      elif "(" in call_word or ")" in clean_call_word:
        call_lemma = "UNK"
        call_word_infos = [['', '', last_call_index]]
        print(f"  - Call: [{call_word}] Lemma: [UNK]")
      else:
        call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == clean_call_word]
        if len(call_word_infos) == 0:
          call_word_infos = [wf for wf in wf_infos if clean_token(wf[0]) == strip_affixes(clean_call_word)]
        assert len(call_word_infos) > 0
        call_lemma = [cw[1] for cw in call_word_infos if cw[-1] >= last_call_index]
        assert len(call_lemma) > 0
      last_call_index = min([cw[-1] for cw in call_word_infos if cw[-1] >= last_call_index])
      DBG and logfd.write("{}\t{}\n".format(call_word, call_lemma[0]))
      #print("  - {} {}".format(call_word, call_lemma[0]))
    logfd.flush()

    # # tokos_for_rhyme_words = [clean_token(txt.text).lower() for txt in tokos_for_rhyme_words]
    # tokos_for_rhyme_words = []
    # no_punct = [toko for toko in poem_ana if not toko.is_punct and not toko.is_space]
    # #breakpoint()
    # for tidx, toko in enumerate(no_punct):
    #   if tidx == len(no_punct) - 1:
    #     tokos_for_rhyme_words.append(toko)
    #   # elif (no_punct[tidx-1].text, no_punct[tidx+1].text) in all_rhyme_contexts:
    #   #
    #   #   tokos_for_rhyme_words.append(toko)
    #   #
    #   elif no_punct[tidx + 1].is_space:
    #     tokos_for_rhyme_words.append(toko)
    # rhyme_words_texts = [clean_token(txt.text).lower() for txt in tokos_for_rhyme_words]
    #
    # #assert len(all_rhyme_words) == len(tokos_for_rhyme_words)
    # #assert len(tokos_for_rhyme_words) == len(rhyme_words_texts)
    #
    # line_nbr = 0
    # all_poem_lemmas = {}
    # for ridx, row in poem_infos.iterrows():
    #   assert row.Text == raw_txt
    #   call_word = row.Call
    #   echo_word = row.Echo
    #   if clean_token(call_word).lower() not in all_rhyme_words:
    #     if tokos_for_rhyme_words[line_nbr].text in cf.clitics:
    #       call_lemma = no_punct[no_punct.index(tokos_for_rhyme_words[line_nbr])-1].lemma_
    #     else:
    #       call_lemma = "##ERROR##"
    #   # assert clean_token(call_word).lower() in all_rhyme_words
    #   # assert clean_token(tokos_for_rhyme_words[line_nbr].text).lower() == clean_token(call_word).lower()
    #   else:
    #     call_lemma = tokos_for_rhyme_words[line_nbr].lemma_
    #   all_poem_lemmas.setdefault(call_word.lower(), [])
    #   all_poem_lemmas[call_word.lower()].append(call_lemma)
    #   if ridx == 1:
    #     print(clean_txt)
    #     # print(raw_txt)
    #   if ridx > 0 and not ridx % 500:
    #     print(f"- Done {ridx} rows [{strftime('%R')}]")
    #   line_nbr += 1

    # add echo
    # consumed_lemma_counts = {rw: 0 for rw in rhyme_words_texts}
    # for ridx, row in poem_infos.iterrows():
    #   echo_word = row.Echo
    #   if echo_word == ' ':
    #     continue
    #   echo_lemma = \
    #     all_poem_lemmas[clean_token(echo_word).lower()][consumed_lemma_counts[clean_token(echo_word).lower()]]
    #   consumed_lemma_counts[clean_token(echo_word).lower()] += 1
      # if clean_token(toko.text.lower()) in
      #assert echo_word.lower() in all_rhyme_words
      # try:
      #   pass
      # except TypeError as e:
      #   print(f" - Error Line {idx}: Line:[] Error:[{repr(e)}]")
      #   continue
    if pidx > 0 and not pidx % 100:
      print(f"- Done {pidx} poems [{strftime('%R')}]")

    if pidx > 10000:
      break
  logfd.close()
