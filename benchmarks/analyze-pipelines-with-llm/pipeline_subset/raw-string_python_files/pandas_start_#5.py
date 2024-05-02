import pandas as pd
import numpy as np

df = pd.read_csv('datasets/titanic_passengers.csv')
print(df)
print()

print('Printando apenas os labels das colunas')
print(df.columns)
print()

print('Printando os dados do index')
print(df.index)
print()

print('Printando apenas os valores únicos de uma coluna')
print(df['Sex'].unique())
print()

print('Printando quantidade por valor')
print('Exemplo: quantas pessoas do sexo feminino no navio?')
print(df['Sex'].value_counts())
print()

print('Aplicando métodos estatísticos')
print('Média de idade: ', df['Age'].mean())
#Existem valores NaN registrados que afetam a idade mínima
print('Idade mínima registrada: ', df['Age'].min())
print('Desvio padrão da idade: ', df['Age'].std())
print('Valor máximo: ', df['Age'].max())
print('Aplicando describe: ', df['Age'].describe())
print()

print('Verificando dados duplicados')
print(df.duplicated()) #Retorna false (0) caso não seja duplicada ou true (1) caso duplicada
#df.duplicated().sum() soma os retornos 1 (true) e me faz visualizar o número de linhas duplicadas
print(df.drop_duplicates()) #método que dropa linhas duplicadas e retorna o dataframe sem elas

print('Realiando uma comparação e verificando seu resultado')
print(df['Age'] > 25)
print()

print('Printando um novo dataframe baseado em uma máscara do anterior')
df2 = df[df['Age'] > 25] #Máscara. Criei uma slice onde eu queria apenas jovens abaixo de 25 anos nesse novo dataframe
print(df2)
print()

print('Criando um novo dataframe baseado em dois dados de uma coluna')
df3 = df[df['Age'] > df['Age'].mean()]
print(df3)

