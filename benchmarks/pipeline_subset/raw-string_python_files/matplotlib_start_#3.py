import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('datasets/houses_to_rent.csv') #Carregand um dataset

#Primeiro, conheça o seu dataset
print(df.head())           #Pegando as 5 primeiras linhas para visualizar o dataset
print(df['city'].unique()) #Pegando os valores únicos da coluna
print(df.shape)            #Pegando a quantidade de linhas x colunas

#Segundo, organize seus dados
#Fazendo dataframes separados para cada cidade
df_saopaulo = df[df['city'] == 'São Paulo']
df_campinas = df[df['city'] == 'Campinas']
df_bh = df[df['city'] == 'Belo Horizonte']
df_rj = df[df['city'] == 'Rio de Janeiro']
df_pa = df[df['city'] == 'Porto Alegre']

#Realizando subplots de outra maneira
figure, axes = plt.subplots(nrows=1, ncols=2, figsize=(14,5))
#Axes - uma lista que guarda os gráficos. Pode ser acessado usando axes[0] por exemplo

axes[0].scatter(df_saopaulo['area'], df_saopaulo['total (R$)'])
axes[0].set_title('São Paulo')
axes[0].set_xlabel('Área (m²)')
axes[0].set_ylabel('R$')
axes[1].bar(df_bh['area'], df_bh['total (R$)'])
axes[1].set_title
axes[1].set_xlabel('Área (m²)')
axes[1].set_ylabel('R$')
plt.show()
#E se eu quiser plotar na posição 3 de um subplot 2x2?
#Simples! A próxima posição depois do axes[1] é axes[0][1]!
#a função plt.subplots faz uma LISTA! então suas posições são acessadas como listas!!!
