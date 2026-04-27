def primeiro_lex(lst):
    '''
    Organiza as palavras em uma lista de forma ordenada pela ordem lexicográfica
    '''

    men_nome = lst[0]
    for k in lst:
        ks = k.strip()
        if ks < men_nome:
            men_nome = ks
    return men_nome
