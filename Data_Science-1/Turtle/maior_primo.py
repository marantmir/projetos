def ehprimo(n):
    div = 0
    k = 2

    while k <= int(n**0.5):     
        if n % k == 0:
            div = div + 1
        k+= 1
                      
    return div == 0


def maior_primo(a):

    while not ehprimo(a):
        a = a - 1
    return a
