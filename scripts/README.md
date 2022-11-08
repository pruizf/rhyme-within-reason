# Scripts

## Corpus Creation

- `add-rhyme-word-and-metadata.xsl`: Identifies rhyme words in Corpus de Sonetos del Siglo de Oro (CSSDO) and adds author metadata
- `add_rhyme_to_adso.py`: Adds rhyme schema to Corpus de Sonetos del Siglo de Oro, with RhymeTagger
- `create-dataframe-cssdo.xsl`: Creates CSSDO dataframe
- `create-dataframe-disco.xsl`: Creates DISCO dataframe

## Annotation
- `config.py`: Annotation configuration
- `remove_duplicate_sonnets.py`: Keeps sonnets that are both in CSSDO and DISCO in CSSDO only, in results dataframes
- `examine_missing_ids.py`: Find sonnets absent from the rhyme-pair dataframe `../data/dataframe-all_lem_sets_emos_with_nrc_filt.tsv`, to analyze the reasons  

### Lemmatization
For rhyme-word lemmatization

- `get_lemmas.py`: Applies Stanza for rhyme-word lemmatization
   - `custom_lemmas.py`: Lemmatization exceptions
- `add_echo_set_lemmas.py`: Adds set of lemmas for the echos of a given call
- `evaluation.py`: selects a sample of lines for manual evaluation, results are at [[annotation/doc]](./annotation/doc)

### Sentiment and emotion

### Lexicon coverage
- `annotation_coverage_details.py`: To determine the extent to which the lexicons cover the corpus
- `print_annotation_coverage.py`: Less detailed than previous script

### Analyses

- `add_emo_pol_to_rhymes.py`: Adds emotion and VAD scores to rhyme words based on lexica in `../lexica` 
- `aggregate_emotions.py`: Get emotion-type counts per-poem for emotion occurrences with scores above a threshold
- `analysis_oct_ses.ipynb`: Compares octave and sestet for emotion scores
- `get_signatures.py`: Gets valence "signature" counts, i.e. counts of valence combinations for each call-word and its echo, aggregated at poem level
- `query.ipynb`: To query corpus dataframe for specific sonnets or sonnet groups
- `recode_emotions_with_threshold.ipynb`: To filter out rhyme-pairs whose emotion scores are below a threshold