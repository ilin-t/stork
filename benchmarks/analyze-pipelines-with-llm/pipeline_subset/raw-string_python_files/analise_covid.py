import pandas as pd
from scipy import stats

##analisar por idade
data21 = pd.read_csv('covid21.csv',sep=',',on_bad_lines="skip",low_memory=False)
data21.dropna(subset=['idade'], inplace=True)
data21.dropna(subset=['raca_cor'],inplace=True)
data21.dropna(subset=['sexo'],inplace=True)
print("Analisando casos leves de covid 2021: ")
geral = pd.to_numeric(data21['idade'],errors="coerce")
mediana = round(geral.median(),2)
media = round(geral.mean(),2)
print("MEDIA E MEDIANA DE IDADE DOS PACIENTES POR CASOS LEVES DE COVID: ")
print("")
print("A média das idade dos pacientes foi: {}".format(str(media)))
print("A mediana das idades dos pacientes foi {}".format(str(mediana)))

##analisando por genero
mulheres_21 = data21[data21['sexo'] == "Feminino"]['idade']
homens_21 = data21[data21['sexo'] == "Masculino"]['idade']
mulheres_21 = pd.to_numeric(mulheres_21,errors='coerce')
homens_21 = pd.to_numeric(homens_21,errors='coerce')
media_homens_21 = homens_21.mean()
mediana_homens_21 = homens_21.median()
media_mulheres_21 = mulheres_21.mean()
mediana_mulheres_21 = mulheres_21.median()
print("A média de idade das mulheres em estado leve foi: {}".format(str(media_mulheres_21)))
print("A mediana de idade das mulheres em estado leve foi: {}".format(str(mediana_mulheres_21)))
print("A média de idade dos homens em estado leve foi: {}".format(str(media_homens_21)))
print("A mediana de idade dos homens em estado leve foi: {}".format(str(mediana_homens_21)))

##2022
print("Dados dos casos leves de covid 2022: ")
data22 = pd.read_csv('covid22.csv',sep=',',on_bad_lines="skip",low_memory=False)
data22.dropna(subset=['idade'], inplace=True)
data22.dropna(subset=['raca_cor'],inplace=True)
data22.dropna(subset=['sexo'],inplace=True)
data22.dropna(subset=['_id'],inplace=True)

geral2 = pd.to_numeric(data22['idade'],errors="coerce")
mediana = round(geral2.median(),2)
media = round(geral2.mean(),2)
print("MEDIA E MEDIANA DE IDADE DOS PACIENTES POR CASOS LEVES DE COVID: ")
print("")
print("A média das idade dos pacientes foi: {}".format(str(media)))
print("A mediana das idades dos pacientes foi {}".format(str(mediana)))

##analisando por genero
mulheres_22 = data22[data22['sexo'] == "Feminino"]['idade']
homens_22 = data22[data22['sexo'] == "Masculino"]['idade']
mulheres_22 = pd.to_numeric(mulheres_22,errors='coerce')
homens_22 = pd.to_numeric(homens_22,errors='coerce')
media_homens_22 = homens_22.mean()
mediana_homens_22 = homens_22.median()
media_mulheres_22 = mulheres_22.mean()
mediana_mulheres_22 = mulheres_22.median()
print("A média de idade das mulheres em estado leve foi: {}".format(str(media_mulheres_22)))
print("A mediana de idade das mulheres em estado leve foi: {}".format(str(mediana_mulheres_22)))
print("A média de idade dos homens em estado leve foi: {}".format(str(media_homens_22)))
print("A mediana de idade dos homens em estado leve foi: {}".format(str(mediana_homens_22)))