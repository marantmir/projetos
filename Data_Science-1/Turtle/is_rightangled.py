def is_rightangled(a, b, c):
    hyp = max([a,b,c])
    return abs(2*hyp**2 - (a**2 + b**2 +c**2)) < 0.001