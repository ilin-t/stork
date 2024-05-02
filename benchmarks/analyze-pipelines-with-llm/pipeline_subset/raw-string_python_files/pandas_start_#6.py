import pandas as pd
import numpy as np
from random import choice as ch #importando um escolhedor de valores

df = pd.read_csv('datasets/iris_dataset.csv')
print(df)
print()

#Criei um numpy array pra adicionar ele depois no dataframe
#Travei o gerador aleatório de array pra não ficar mudando a cada execução
#       V           Pedi para ele me gerar 150 valores aleatórios entre 0 e 1
#       V               V
np.random.seed(2)   #   V
root_lenght = np.random.rand(150)
print(root_lenght)
print()

print('Adicionando root lenght dentro do dataframe')
#Adicionando nova coluna:
#Primeiro, eu "finjo" tentar acessar ela e crio um nome pra ser exibido na coluna
#  V                Depois eu indico de qual variável esse valor vai sair 
#  V                    V
df['root_lenght'] = root_lenght
#printando pra saber se a coluna já foi adicionada
print(df)
print()

#lembrar que a quantidade do range TEM que ser igual à quantidade da dimensão em que quero incluir a coluna
#linha/coluna
plant_sex = [ch(['M', 'F']) for i in range (150)]
print(plant_sex)
print()

df['plant_sex'] = plant_sex
print(df)
print()

print('Deletando uma linha')
df.drop(0)
print(df.drop(0))
print()

#Esse delete de coluna é simplesmente uma espécie de slice
#Basicamente eu filtrei um resultado e o seu retorno é mostrado no print desse método
#Droppando uma coluna:
#       V
#df = (df.drop['plant_sex'], axis = 1)

print('Droppando uma coluna')
#Para mostrar a coluna após o drop, é necessário jogar o método inteiro na função print
#   V   Por padrão, ele busca deletar o label declarado nas linhas, mas o axis=1 informa para buscar uma coluna
#   V                           V      Inplace, caso "true", substitui o dataframe pelo dataframe filtrado.
#   V                           V        Por padrão ele é "false".
#   V                           V           V
print(df.drop(['plant_sex'], axis=1, inplace=True))
print(df)

