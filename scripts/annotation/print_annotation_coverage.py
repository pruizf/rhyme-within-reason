"""
Prints percentage of available and missing values for annotation type.
"""

import pandas as pd
import sys

#import config as cf

cdf_fn = sys.argv[1]

cdf = pd.read_csv(cdf_fn, sep="\t")

# print summary
pd.options.display.float_format = "{:,.2f}".format
pd.set_option('display.max_rows', 70)
percent_missing = cdf.isnull().sum() * 100 / len(cdf)
percent_available = 100 - percent_missing
missing_value_df = pd.DataFrame({'column_name': cdf.columns,
                                 'percent_available': percent_available,
                                 'percent_missing': percent_missing})
print(missing_value_df)
#missing_value_df.to_csv(cf.df_coverage_path, sep="\t", index=False)