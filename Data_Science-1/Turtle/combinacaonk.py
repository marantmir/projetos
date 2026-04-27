def fatorial(n):
    fat = 1
    while n > 1:
        fat = fat * n
        n = n -1
    return fat

def combinacao(m,n):
    return fatorial(m)//(fatorial(m-n)*fatorial(n))

print(fatorial(5))

print(combinacao(20,10))
