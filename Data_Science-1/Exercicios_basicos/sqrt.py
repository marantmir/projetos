def sqrt(x):

    aprox = 0.5*x
    better = 0.5*(aprox + x/aprox)

    while abs(aprox-better) > 0.0001:
        aprox = better
        better = 0.5*(aprox + x/aprox)
        print(better)
    return better
    
