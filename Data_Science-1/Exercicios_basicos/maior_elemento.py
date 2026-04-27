def maior_elemento(lista):
    '''
    Função que recebe como parâmetro uma lista com números inteiros e devolve 
    um número inteiro correspondente ao maior valor presente na lista recebida.
    '''
    maior = lista[0]
    for k in lista:
        if k > maior:
            maior = k
    return maior
