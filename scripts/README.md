## Corpus Creation

- `add-rhyme-word-and-metadata.xsl`: Identifies rhyme words in Corpus de Sonetos del Siglo de Oro (CSSDO) and adds author metadata
- `add_rhyme_to_adso.py`: Adds rhyme schema to Corpus de Sonetos del Siglo de Oro, with RhymeTagger
- `create-dataframe-cssdo.xsl`: Creates CSSDO dataframe
- `create-dataframe-disco.xsl`: Creates DISCO dataframe

## Annotation
- `config.py`: Annotation configuration

### Lemmatization
For rhyme-word lemmatization

- `get_lemmas.py`: Applies Stanza for rhyme-word lemmatization
   - `custom_lemmas.py`: Lemmatization exceptions
- `add_echo_set_lemmas.py`: Adds set of lemmas for the echos of a given call
- `evaluation.py`: selects a sample of lines for manual evaluation

### Sentiment and emotion

- `add_emo_pol_to_rhymes.py`: Adds emotion and VAD scores to rhyme words based on lexica in `../lexica` 
- `get_signatures.py`: Gets valence "signature" counts, i.e. counts of valence combinations for each call-word and its echo, aggregated at poem level