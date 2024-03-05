import os

import pandas as pd

import plot_libraries as pl

def get_yearly_participation(library, start_year, end_year, repo_counts):

    lib_counts = pl.aggregate_counts_per_year(library=library, start_year=start_year, end_year=end_year)
    ratios={}
    for i in range(start_year, end_year+1):
        ratios[i] = (lib_counts['count'][i]/repo_counts[i]) * 100

    ratios_df = pd.DataFrame.from_dict(data=ratios, orient='index', columns=['count'])
    print(ratios_df)

    return ratios_df


repo_counts = {2018 : 65648, 2019: 65448, 2020: 54924, 2021: 115288, 2022: 107436, 2023: 85785}
numpy_pct = get_yearly_participation('numpy', 2018, 2023, repo_counts)
pandas_pct = get_yearly_participation('pandas', 2018, 2023, repo_counts)
tf_pct = get_yearly_participation('tensorflow', 2018, 2023, repo_counts)
scipy_pct = get_yearly_participation('scipy', 2018, 2023, repo_counts)
# sql_pct = get_yearly_participation('sqlalchemy', 2018, 2023, repo_counts)
torch_pct = get_yearly_participation('torch', 2018, 2023, repo_counts)
sk_learn_pct = get_yearly_participation('scikit_learn', 2018, 2023, repo_counts)
keras_pct = get_yearly_participation('keras', 2018, 2023, repo_counts)

dm_libs = ['numpy', 'pandas', 'scipy']
ml_libs = ['sklearn', 'tensorflow', 'keras', 'torch']

pl.plot_lines_df(df_list=[sk_learn_pct, tf_pct, keras_pct, torch_pct], libgroup='ml_pct', libs = ml_libs)