def imprime_matriz(mat):
    """
    Função para imprimir a matriz na forma de melhor visualização
    """
    linhas = len(mat)
    colunas = len(mat[0])
    
    for k in range(linhas):
        for j in range(colunas):
            if j == colunas-1:
                print(mat[k][j])
            else:
                print(mat[k][j],end = " ")
