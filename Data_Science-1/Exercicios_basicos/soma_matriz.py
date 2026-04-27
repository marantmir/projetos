def dimensoes2(matriz):
    """
    função dimensoes(matriz) que recebe uma matriz como parâmetro e 
    retorna as dimensões da matriz recebida, no formato de tupla (i,j).
    """
    return len(matriz),len(matriz[0])

def soma_matrizes(m1, m2):
    """
    função soma_matrizes(m1, m2) que recebe 2 matrizes e devolve uma matriz 
    que represente sua soma caso as matrizes tenham dimensões iguais. 
    Caso contrário, a função deve devolver False.
    """
    msoma = m1.copy()
    
    linhas,colunas = dimensoes2(m1)
    
    if dimensoes2(m1) != dimensoes2(m2):
        return False
    else:
        for k in range(linhas):
            for j in range(colunas):
                msoma[k][j] = m1[k][j] + m2[k][j]
                
    return msoma
