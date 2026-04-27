def ordenada(lista):
    for i,k in enumerate(lista[:-1]):
        if k > lista[i+1]:
            return False
    return True
