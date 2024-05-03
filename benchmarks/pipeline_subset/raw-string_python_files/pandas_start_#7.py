import pandas as pd
import numpy as np

dados = np.array([[ 1,  2,  np.nan],
                 [12,  np.nan,  np.nan],
                 [ 3,  5,  2]])
print(dados)
print()

df = pd.DataFrame(dados, columns='A B C'.split())
print(df)
print()

#retorna true para quando o dado na tabela é nulo e false para o contrário
print(df.isnull())
print()
#printando uma coluna para saber seus dados ausentes
print(df['A'].isnull())
print()

#droppando linhas com resultados nulos
#atenção: se a linha tiver pelo menos 1 único resultado ausente, ela é completamente eliminada
#o resultado final são sempre as linhas sem resultados ausentes
print(df.dropna())
print()
#para eu fazer com que o dropna seja definitivo eu preciso codar: df = df.dropna()
#logo a partir dessa linha, df excluirá definitivamente as linhas
print(df)
print()

#preenchendo os dados ausentes de linhas com um valor preestabelecido
#lembrando que ela segue a mesma regra do dropna para ser definitivo
#é mais comum utilizada para preencher colunas
#é interessante substituir por valores próximos de valores anteriores ou posteriores
print(df.fillna(0))
print()
print(df.fillna(method='bfill'))
print()

#Lendo e estruturando os dados do titanic realizados anteriormente
#Chamei o DataFrame de ttn
ttn = pd.read_csv('datasets/titanic_passengers.csv')
print(ttn)

#Somando os elementos nulos de cada coluna
print(ttn.isnull().sum())
#Por favor, lembrar que SUM é uma somatória geral e value_counts() conta a quantidade de elementos distintos em uma Series
#Sum agrupou diretamente como colunas
print()
print(ttn.drop('Cabin', axis=1, inplace=True))
print(ttn.columns)
print()
#Dentro de Fare existe um valor em branco. Dentro de tantas linhas, apenas uma possui esse formato
#Por isso não vale a pena deletar essa coljuna e sim preencher o espaço vazio
#Como são poucos dados, sibstitui pelo valor que mais aparece
print(ttn['Fare'].value_counts())
print()
#Preenchendo com o espaço vazio
#Função para preencher o espaço
#               V   Valor que será colocado dentro dos espaços vazios
#               V     V        Vai substituir o DataFrame original?
#               V     V         V
ttn['Fare'].fillna(7.7500, inplace=True)
print(ttn.isnull().sum())
print()

#Na coluna de idade temos dados consideravelmente nulos, mas não é toda a coluna que está condenada
#para não perder os dados já preenchidos vamos substituir pela média das idades

ttn['Age'].fillna(ttn['Age'].mean(), inplace=True)
print(ttn.isnull().sum())
print()
print(ttn['Age'].value_counts())
