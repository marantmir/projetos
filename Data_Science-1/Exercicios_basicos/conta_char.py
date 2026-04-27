def conta_letras(frase, contar = "vogais"):
    cnt = 0
    
    frase = frase.upper()
    
    if contar == "vogais":
        for k in frase:
            if k in 'AEIOU':
                cnt += 1
    else:
        lst_cons = [chr(x) for x in range(65,91) if chr(x) not in 'AEIOU']
        for k in frase:
            if k in lst_cons:
                cnt += 1
    return cnt
