import pandas as pd
import numpy as np

#Eu criei esse dataser em csv, mas a coluna do index foi impressa junto
#Se eu printar o DataFrame nesse momento, o index vai ser acrescido como COLUNA
df_covid = pd.read_csv('datasets/covid_exemplo.csv')
#Droppando a coluna index que veio por acidente
df_covid.drop(['Unnamed: 0'], axis=1, inplace=True)

#Quando eu agrupo os dados de uma coluna, ele não vai saber o que fazer com
#as informações presente nas outras e por isso o resultado de um print nesse momento é um erro.
#   Para fazer o groupby funcionar, eu devo passar um método pros outros dados
#   Exemplo:
df_covid = df_covid.groupby('Teve COVID?')
#passando um método pro gruopby funcionar
print(df_covid.mean())
print()

## DATASET TITANIC ##
df = pd.read_csv('datasets/titanic_passengers.csv')
df_survived = df.groupby('Survived')

#Ao somar o DataFrame em funções, as colunas de dados categóricos como textos, somem!!
#Pegando as médias dos dados de pessoas que sobreviveram
print(df_survived.mean())

#Pegando as médias dos dados agrupados por Sexo
df_sex = df.groupby('Sex').mean()
print(df_sex)

#Pegando o desvio padrão dos dados do agrupamento por Sexo
print(df.groupby('Sex').std())
