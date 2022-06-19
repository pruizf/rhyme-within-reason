"""Get counts of high emotion call words"""

from importlib import reload
import numpy as np
import pandas as pd
from time import strftime
import warnings


import config as cf

threshold = 0.6

if __name__ == "__main__":
  cdf = pd.read_csv(cf.df_emos, sep="\t")
  # filter above or equal to threshold
  highemo = cdf.loc[(cdf['joy_call'] >= threshold) | (cdf['sadness_call'] >= threshold) |
                    (cdf['anger_call'] >= threshold) | (cdf['fear_call'] >= threshold) |
                    (cdf['disgust_call'] >= threshold)]
  highemo_g = highemo.groupby('SonnetID')
  # get series with counts
  joy = highemo_g.apply(lambda x: x[x['joy_call'] >= threshold]['joy_call'].count())
  sadness = highemo_g.apply(lambda x: x[x['sadness_call'] >= threshold]['sadness_call'].count())
  anger = highemo_g.apply(lambda x: x[x['anger_call'] >= threshold]['anger_call'].count())
  fear = highemo_g.apply(lambda x: x[x['fear_call'] >= threshold]['fear_call'].count())
  disgust = highemo_g.apply(lambda x: x[x['disgust_call'] >= threshold]['disgust_call'].count())
  # get dataframes
  joy_df = joy.to_frame()
  sadness_df = sadness.to_frame()
  anger_df = anger.to_frame()
  fear_df = fear.to_frame()
  disgust_df = disgust.to_frame()
  # name columns
  joy_df.columns = ['joy']
  sadness_df.columns = ['sadness']
  anger_df.columns = ['anger']
  fear_df.columns = ['fear']
  disgust_df.columns = ['disgust']
  # merge
  merged = pd.merge(joy_df, sadness_df, on='SonnetID')
  merged = pd.merge(merged, anger_df, on='SonnetID')
  merged = pd.merge(merged, fear_df, on='SonnetID')
  merged = pd.merge(merged, disgust_df, on='SonnetID')
  merged.to_csv(cf.highemo_counts.format(
    str(threshold).replace(".", "")), sep='\t')
