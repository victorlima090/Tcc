# By Klenilmar Dias
# Script desenvolvido para Treinar um Modelo para o  Classificador Online 

from sklearn import svm

# O modulo JOBLIB permitira salvar um modelo de treinamento no arquivo e carrega-lo posteriormente
from sklearn.externals import joblib
import re


# Matriz de Rotulos de Classe para Treinamento
category = []

# Matriz com as Caracterisitcas (features) para Treinamento
featureMatrix = []

# Abre a Matriz de Rotulos de Classe em um objeto arquivo (cat_file) com a funcao "open" utilizando o argumento"r" que diz que queremos abrir o arquivo para leitura
cat_file = open("category.dat", "r")

# Aplica um loop (for) para ler o arquivo linha por linha
for line in cat_file:
    category.append(int(line)) # Em vez de ler uma linha por vez, podemos carregar todas as linhas em uma lista de strings (linhas)


# Abre a Matriz de Caracteristicas (features) em um objeto arquivo (fm_file) com a funcao "open" utilizando o argumento"r" que diz que queremos abrir o arquivo para leitura
fm_file = open("featureMatrix.dat", "r")

# Aplica um loop (for) para ler o arquivo linha por linha
for line in fm_file:
    nums = [float(n) for n in line.split()] # Converte cada linha em um "float" e utiliza o recurso "split" para dividir a string em numeros separadas por espacos em branco
    featureMatrix.append(nums) # Em vez de ler uma linha por vez, podemos carregar todas as linhas em uma lista de strings (linhas)

print "Modelo de Treinamento"

# Cria um Modelo Classificador SVM (Support Vector Machines)
model = svm.SVC(cache_size=1000, class_weight='balanced')

# Treina (ajusta=fit) o Modelo usando os conjuntos de Treinamento
model.fit(featureMatrix, category) # Realiza o ajuste da featureMatrix de acordo com category (Treina o Classificador)

print "Modelo de Classificacao Treinado"
print model


# Persistir o modelo do classificador treinado (utiza para isso a funcao dump) em um arquivo denominado de model.pkl
joblib.dump(model, 'model/model.pkl')

