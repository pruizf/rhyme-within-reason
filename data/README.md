# Data

- `dataframe-cssdo.tsv`: Corpus de Sonetos del Siglo de Oro
- `dataframe-disco.tsv`: DISCO (Golden Age subcorpus)
- `dataframe-all.tsv`: Both corpora
- `dataframe-all_lem_sets.tsv`: Call word and echo lemmas added to `dataframe-all.tsv`
- `dataframe-all_lem_sets_emos.tsv`: VAD (valence, arousal, dominance) an affect scores added to preceding
- `signatures.tsv`: call-echo signatures in valence terms
- `highemos_XX_counts_per_poem.tsv`: emotion-type counts per poem for emotion words with score >= XX
- Files `filenames_cssdo.txt`, `filenames_disco_only_new_IDs.txt` and `ids_to_keep.txt` were used to keep sonnets duplicated across CSSDO and DISCO only as part of CSSDO
- Filenames ending with `_filt.tsv` are the result of the deduplication mentioned in the previous point

# Conventions

## Valence signatures:
- 0: negative (< 0.5 after scaling)
- 1: positive (>= 0.5 after scaling)
- 9: term not found in the lexica