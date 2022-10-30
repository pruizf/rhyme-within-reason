"""
Prints details for lexicon coverage of rhyme words (sentiment and emotion)
at occurrence and vocabulary levels.
"""

import os
import pandas as pd

data = "../../data/dataframe-all_lem_sets_emos_with_nrc_filt.tsv"

"""
- find nbr of occurrences
- find nbr of occurrences with annotations
- find vocabulary (value_counts)
- find vocabulary for those which have annotations (value_counts again)

do this for
- valence (before using NRC)
- valence (once use NRC)

- emotion (before using NRC)
- emotion (once use NRC)
"""

df = pd.read_csv(data, sep="\t")

# values common to all calculations
#  uniques
uniq_lemmas = df['CallLemma'].value_counts()
nb_uniq_lemmas = len(uniq_lemmas)
#  occurrences
#  ensure that there's no null values on CallLemma column
assert len(df.CallLemma) == len(df.loc[~(df.CallLemma).isna()])
nb_lemmas = len(df['CallLemma'])


print("# Sentiment")
print("## Call lemmas with annotations vs. vocabulary")
print(f"  - Unique lemmas: {nb_uniq_lemmas}")
lemmas_with_vad = df.loc[df['call_in_vad'] == 1, 'CallLemma']
nb_lemmas_with_vad = len(lemmas_with_vad.value_counts())
ratio_vad_uniq_lemmas = 100*nb_lemmas_with_vad/nb_uniq_lemmas
print(f"  - Lemmas with Stadthagen VAD score: {nb_lemmas_with_vad}, " +
      f"{ratio_vad_uniq_lemmas:.2f}% of unique lemmas")
# NVAD score only available if Stadthagen does not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_nvad = df.loc[df['call_in_nvad'] == 1, 'CallLemma']
nb_lemmas_with_nvad = len(lemmas_with_nvad.value_counts())
ratio_nvad_uniq_lemmas = 100*nb_lemmas_with_nvad/nb_uniq_lemmas
cumulative = ratio_vad_uniq_lemmas+ratio_nvad_uniq_lemmas
print(f"  - Lemmas (additional) with NRC VAD score: +{nb_lemmas_with_nvad}" +
      f" ({nb_lemmas_with_vad+nb_lemmas_with_nvad}), " +
      f"{ratio_nvad_uniq_lemmas:.2f}% of unique lemmas, " +
      f"cumulative: {cumulative:.2f}%")
# MLS score only available if Stadthagen and NRC do not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_mls = df.loc[df['call_in_mls'] == 1, 'CallLemma']
nb_lemmas_with_mls = len(lemmas_with_mls.value_counts())
ratio_mls_uniq_lemmas = 100*nb_lemmas_with_mls/nb_uniq_lemmas
cumulative += ratio_mls_uniq_lemmas
print(f"  - Lemmas (additional) with MLS score: +{nb_lemmas_with_mls} " +
      f"{ratio_mls_uniq_lemmas:.2f}% of unique lemmas, " +
      f" ({nb_lemmas_with_vad + nb_lemmas_with_nvad+nb_lemmas_with_mls}), " +
      f"cumulative: {cumulative:.2f}%")

print("## Occurrences of call lemmas with annotations vs. total call-lemma occurrences")
print(f"  - Number of lemma occurrences: {nb_lemmas}")
lemmas_with_vad = df.loc[df['call_in_vad'] == 1, 'CallLemma']
nb_lemmas_with_vad = len(lemmas_with_vad)
ratio_vad_lemmas = 100*nb_lemmas_with_vad/nb_lemmas
print(f"  - Lemmas with Stadthagen VAD score: {nb_lemmas_with_vad}, " +
      f"{ratio_vad_lemmas:.2f}% of lemma occurrences")
# NVAD score only available if Stadthagen does not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_nvad = df.loc[df['call_in_nvad'] == 1, 'CallLemma']
nb_lemmas_with_nvad = len(lemmas_with_nvad)
ratio_nvad_lemmas = 100*nb_lemmas_with_nvad/nb_lemmas
cumulative = ratio_vad_lemmas+ratio_nvad_lemmas
print(f"  - Lemmas (additional) with NRC VAD score: +{nb_lemmas_with_nvad} " +
      f"({nb_lemmas_with_vad + nb_lemmas_with_nvad}), " +
      f"{ratio_nvad_lemmas:.2f}% of lemma occurrences, " +
      f"cumulative: {cumulative:.2f}%")
# MLS score only available if Stadthagen and NRC do not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_mls = df.loc[df['call_in_mls'] == 1, 'CallLemma']
nb_lemmas_with_mls = len(lemmas_with_mls)
ratio_mls_lemmas = 100*nb_lemmas_with_mls/nb_lemmas
cumulative += ratio_mls_lemmas
print(f"  - Lemmas (additional) with MLS score: +{nb_lemmas_with_mls} " +
      f"({nb_lemmas_with_vad + nb_lemmas_with_nvad + nb_lemmas_with_mls}), " +
      f"{ratio_mls_lemmas:.2f}% of lemma occurrences, " +
      f"cumulative: {cumulative:.2f}%")


print("\n# Emotion")
print("## Call lemmas with annotations vs. vocabulary")
print(f"  - Unique lemmas: {nb_uniq_lemmas}")
lemmas_with_ei = df.loc[df['call_in_ei'] == 1, 'CallLemma']
nb_lemmas_with_ei = len(lemmas_with_ei.value_counts())
ratio_ei_uniq_lemmas = 100*nb_lemmas_with_ei/nb_uniq_lemmas
print(f"  - Lemmas with Stadthagen EI score: {nb_lemmas_with_ei}, " +
      f"{ratio_ei_uniq_lemmas:.2f}% of unique lemmas")
# NRC EI score only available if Stadthagen does not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_nei = df.loc[df['call_in_nei'] == 1, 'CallLemma']
nb_lemmas_with_nei = len(lemmas_with_nei.value_counts())
ratio_nei_uniq_lemmas = 100*nb_lemmas_with_nei/nb_uniq_lemmas
cumulative = ratio_ei_uniq_lemmas+ratio_nei_uniq_lemmas
print(f"  - Lemmas (additional) with NRC EI score: +{nb_lemmas_with_nei} " +
      f"({nb_lemmas_with_ei+nb_lemmas_with_nei}), " +
      f"{ratio_nei_uniq_lemmas:.2f}% of unique lemmas, " +
      f"cumulative: {cumulative:.2f}%")

print("## Occurrences of call lemmas with annotations vs. total call-lemma occurrences")
print(f"  - Number of lemma occurrences: {nb_lemmas}")
lemmas_with_ei = df.loc[df['call_in_ei'] == 1, 'CallLemma']
nb_lemmas_with_ei = len(lemmas_with_ei)
ratio_ei_lemmas = 100*nb_lemmas_with_ei/nb_lemmas
print(f"  - Lemmas with Stadthagen ei score: {nb_lemmas_with_ei}, " +
      f"{ratio_ei_lemmas:.2f}% of lemma occurrences")
# NRC EI score only available if Stadthagen does not yield any,
# see way this is computed in :obj:`add_emo_pol_to_rhymes`
lemmas_with_nei = df.loc[df['call_in_nei'] == 1, 'CallLemma']
nb_lemmas_with_nei = len(lemmas_with_nei)
ratio_nei_lemmas = 100*nb_lemmas_with_nei/nb_lemmas
cumulative = ratio_ei_lemmas+ratio_nei_lemmas
print(f"  - Lemmas (additional) with NRC ei score: +{nb_lemmas_with_nei} " +
      f"({nb_lemmas_with_ei + nb_lemmas_with_nei}), " +
      f"{ratio_nei_lemmas:.2f}% of lemma occurrences, " +
      f"cumulative: {cumulative:.2f}%")
