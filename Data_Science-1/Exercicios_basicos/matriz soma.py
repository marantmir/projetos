def soma_matrizes(m1,m2):
    def dimensoes(matriz):
        linhas =len(matriz[:])
        colunas =len(matriz[0])
        dim=str(linhas)+"X"+str(colunas)
        return dim
    if dimensoes(m1)!=dimensoes(m2):
        return (False)

    matriz_soma=[]
    for i in range(len(m1)):
       linha=[]
       for j in range(len(m1[0])):
            linha.append(m1[i][j]+m2[i][j])
       matriz_soma.append(linha)
    return matriz_soma


import random

def cria_matriz(m,n):
    """
    Cria uma matriz mx n com elementos eleatórios
    """
    lista = []
    for _ in range(m):
        linha = []
        for k in range(n):
            linha.append(random.randint(1,100))
        lista.append(linha)
    return lista
            
