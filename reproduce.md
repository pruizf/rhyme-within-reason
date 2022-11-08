# Result reproduction

This reproduces the result in our preprint.

Scripts are in [scripts](./scripts).

## Corpus preprocessing

Scripts are in [scripts/corpus_creation](./scripts/corpus_creation).

First create the corpus dataframes from the corpus TEI, with XSLT.

For the ADSO corpus, first preprocess the corpus to add rhyme words:

```bash
python add_rhyme_to_adso.py

mkdir datatemp
saxon -s:source/cssdo/source_with_rhyme -xsl:add-rhyme-word-and-metadata.xsl -o:datatemp
mv datatemp data
```

Create the ADSO corpus initial dataframe (replace saxon with the command tu run the Saxon XSLT parser on your system):

```bash
saxon -s:source/cssdo/source_with_rhyme -xsl:create-dataframe-cssdo.xsl -o:data
```

Create the DISCO corpus initial dataframe:

```bash
saxon -s:source/cssdo/source_with_rhyme -xsl:create-dataframe-disco.xsl -o:data
```

Both dataframes were concatenated into a single dataframe named `data/dataframe-all.tsv`

## Sentiment and emotion annotation

Scripts are in [scripts/annotation](scripts/annotation)

Input and output paths are in `config.py`.

First add the rhyme-word lemmas. This will output dataframe `data/dataframe-all_lem.tsv`

```bash
python get_lemmas.py
```

Based on the output of the previous command, add echo-chains to the dataframe (rhyme-words sharing the same rhyme). This outputs dataframe `data/dataframe-all_lem_sets.tsv` 

```bash
python add_echo_set_lemmas.py
```

Based on the output of the previous command, add sentiment and emotion values for the rhyme-word lemmas.

This will output dataframe `data/dataframe-all_lem_sets_emos_with_nrc.tsv`

```bash
python add_emo_pol_to_rhymes.py
```

Based on the dataframe output by the previous step, filter out lines for DISCO sonnets that are also part of ADSO. This will output dataframe `data/dataframe_all_lem_sets_emos_with_nrc_filt.tsv`

## Analyses

Tables 1 and 2 regarding rhyme-word coverage by the different lexicons are obtained as follows:

```python
python annotation_coverage_details.py
```

The data thanks to which the results in Box 2 were selected (filtering data as described in section 5.3) are in `data/octave_vs_sestet_merged_octvalmin6_sesvalmin_5_octaromin_6_sesaromin_4_only_86.tsv` 

The data and code for Table 4 and for the boxplots in Figure 6 are in `scripts/annotation_redo_strict.ipynb` 

%TODO: Share data for Table 3 and Figures 2 through 5.


