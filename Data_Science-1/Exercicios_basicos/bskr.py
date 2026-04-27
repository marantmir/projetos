def deltaq2(a,b,c):
    return b**2-4*a*c


def rseq2(a,b,c):
    dt = deltaq2(a,b,c)
    if dt == 0:
        return (-b/(2*a))
    elif dt > 0:
        return ((-b+dt)/(2*a), (-b-dt)/(2*a))
    else:
        return 'Equação sem razizes reais, delta negativo'