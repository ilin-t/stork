import pandas as pd
from scipy import stats
print("ANALISE DE DADOS DE RECEITAS 2021: ")
data_2020 = pd.read_csv('receitas-2021_12-03-2022_16-24-50.csv',sep=',',
                   on_bad_lines='skip', low_memory=False)
data_2020.dropna(subset=['VALOR_RECEITA'],inplace=True)
data_2020 = data_2020['VALOR_RECEITA']
data_2020 = pd.to_numeric(data_2020,errors="coerce")
mediana = data_2020.median()
media = round(data_2020.mean(),2)

print("A mediana foi {}".format(str(mediana)))
print("A media foi {}".format(str(media)))

print("ANALISE DE DADOS DE RECEITAS 2022: ")

data_2021 = pd.read_csv('receitas-2022_06-02-2023_14-23-08.csv',sep=',',
                   on_bad_lines='skip', low_memory=False)
data_2021.dropna(subset=["VALOR_RECEITA"],inplace=True)
data_2021 = data_2021['VALOR_RECEITA']
data_2021 = pd.to_numeric(data_2021,errors="coerce")
mediana = data_2021.median()
media = round(data_2021.mean(),2)
print("A media foi {}".format(str(media)))
print("A mediana foi {}".format(str(mediana)))

t_stat, p_value = stats.ttest_ind(
    data_2021, data_2020, equal_var=False)

# # Print results
print("t-statistic:", t_stat)
print("p-value:", p_value)
# p-value de 0.05