ano = int(input("Digite o número para verificar se ele é bissexto:"))

def isLeap(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                ret = True
            else:
                ret = False
        else:
            ret = True
               
    else:
        ret = False
    return ret

bissexto = isLeap(ano)

if bissexto:
    print("O ano de ",ano,"é bissexto")
