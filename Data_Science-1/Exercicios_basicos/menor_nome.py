def menor_nome(lst):

    men_nome = lst[0]
    for k in lst:
        ks = k.strip()
        if len(ks) < len(men_nome):
            men_nome = ks
    return men_nome.capitalize()
