def ordena(lista):
    fim = len(lista)
    for k in range(fim-1):
        for j in range(k+1,fim):
            if lista[j] < lista[k]:
                lista[k],lista[j] = lista[j],lista[k]
    return lista
