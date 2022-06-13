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

#TODO
# read df
# read and split text into lines
# find call and echo as the last word of each line
# get lemmas for each
# write the lemmas to the dataframe
# write df out


def clean_token(tk):
  tk = re.sub("-$", "", tk)
  tk = tk.replace("?", "")
  return tk


if __name__ == "__main__":
  print(f"- Start [{strftime('%R')}]")
  #snlp = stanza.Pipeline(lang="es", processors="tokenize,pos")
  nlp = spacy.load(cf.spacy_model)
  #nlp = StanzaLanguage(snlp)
  #nlp = spacy_stanza.load_pipeline("es", processors="tokenize,pos,lemma")
  df = pd.read_csv(cf.df_path, sep="\t", index_col=None)
  poem_ids = df['SonnetID'].unique()
  # nan not equal to itself
  poem_ids = list(filter(lambda pid: pid==pid, poem_ids))
  for pidx, poem_id in enumerate(poem_ids):
    poem_infos = df.loc[df['SonnetID'] == poem_id]
    # get poem text
    raw_txt = poem_infos['Text'].iloc[0]
    all_lines = []
    all_rhyme_words = []
    all_rhyme_contexts = []
    stanzas = re.split(r"#+", raw_txt)
    # store rhyme word-forms
    for stz in stanzas:
      lines = [l.strip() for l in re.split(r"~+", stz)]
      all_lines.extend(lines)

    line_anas = [nlp(l) for l in all_lines]
    line_words = [[tok.text for tok in ana if not tok.is_punct and not tok.is_space]
                  for ana in line_anas]
    rhyme_words = [clean_token(line[-1]).lower() for line in line_words]
    all_rhyme_words.extend(rhyme_words)
    all_rhyme_contexts = {}
    for idx, line_for_context in enumerate(line_words):
      if idx == len(line_words) - 1:
        all_rhyme_contexts[(line_for_context[-2], None)] = line_for_context[-1]
      # elif line_for_context[-1] in ("me", "te", "se", "nos", "os", "vos", "le",
      #                               "lo", "les", "los", "la", "las"):
      #
      else:
        all_rhyme_contexts[(line_for_context[-2], line_words[idx+1][0])] = line_for_context[-1]

    # reanalyze poem with complete text (for context before and after rhyme)
    clean_txt = "\n".join(all_lines)
    poem_ana = nlp(clean_txt)
    # tokos_for_rhyme_words = [clean_token(txt.text).lower() for txt in tokos_for_rhyme_words]
    tokos_for_rhyme_words = []
    no_punct = [toko for toko in poem_ana if not toko.is_punct and not toko.is_space]
    #breakpoint()
    for tidx, toko in enumerate(no_punct):
      if tidx == len(no_punct) - 1:
        tokos_for_rhyme_words.append(toko)
      elif (no_punct[tidx-1].text, no_punct[tidx+1].text) in all_rhyme_contexts:

        tokos_for_rhyme_words.append(toko)
      #
      # elif no_punct[tidx + 1].is_space:
      #   tokos_for_rhyme_words.append(toko)
    rhyme_words_texts = [clean_token(txt.text).lower() for txt in tokos_for_rhyme_words]

    assert len(all_rhyme_words) == len(tokos_for_rhyme_words)
    assert len(tokos_for_rhyme_words) == len(rhyme_words_texts)

    line_nbr = 0
    all_poem_lemmas = {}
    for ridx, row in poem_infos.iterrows():
      assert row.Text == raw_txt
      call_word = row.Call
      echo_word = row.Echo
      if clean_token(call_word).lower() not in all_rhyme_words:
        if tokos_for_rhyme_words[line_nbr].text in cf.clitics:
          call_lemma = no_punct[no_punct.index(tokos_for_rhyme_words[line_nbr])-1].lemma_
        else:
          call_lemma = "##ERROR##"
      # assert clean_token(call_word).lower() in all_rhyme_words
      # assert clean_token(tokos_for_rhyme_words[line_nbr].text).lower() == clean_token(call_word).lower()
      else:
        call_lemma = tokos_for_rhyme_words[line_nbr].lemma_
      all_poem_lemmas.setdefault(call_word.lower(), [])
      all_poem_lemmas[call_word.lower()].append(call_lemma)
      if ridx == 1:
        print(clean_txt)
        # print(raw_txt)
      if ridx > 0 and not ridx % 500:
        print(f"- Done {ridx} rows [{strftime('%R')}]")
      line_nbr += 1

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
    if pidx > 100:
      break
