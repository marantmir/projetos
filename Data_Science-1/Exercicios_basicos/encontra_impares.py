def encontra_impares(lista):
    if len(lista) == 1:
        return lista if lista[0] % 2 == 1 else []
    else:
        k = lista[:1] if lista[0] % 2 == 1 else []
        k.extend(encontra_impares(lista[1:]))
        return k
