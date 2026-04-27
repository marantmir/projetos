def ehprimo(n):
    k = 2
    
    while n % k != 0 and k <= int(n**0.5): 
        k+= 1
                      
    return n % k != 0 or n == 2

def n_primos(n):
    '''
    Função que conta quantos primos menores que n existem 
    '''
    
    cnt = 0
    while n >= 2:
        if ehprimo(n):
            cnt+=1
        n+=-1
    return cnt

def n_primeiros_primos(n):
    k = cnt = 0
    while k < n:
        cnt+=1
        if ehprimo(cnt):
            print(cnt,end=",")
            k+=1

