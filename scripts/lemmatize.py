import stanza
import pandas as pd
#stanza.download(lang='es')
nlp = stanza.Pipeline(lang='es')
inputf = pd.read_csv('../data/dataframe-disco.tsv', sep="\t")
columns = []
for column in inputf:
    columns.append(inputf[column].tolist())
poems = columns[9]
calls = columns[10]
#echo = columns[11]
for index,poem in enumerate(poems):
    doc = nlp(poem)
    call = calls[index]
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.text == call:
                print(word.lemma)
