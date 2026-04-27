def main():
    n = int(input("Entre com o expoente da expansão binomial: "))
            
    for k in range(n+1):
        
        print("Coeficiente de x^%d y^%d: %d"%(n-k, k, combinacao(n, k)))
        

def fatorial(k):
    '''(int) -> int

    Recebe um inteiro k e retorna o valor de k!

    Pre-condicao: supoe que k eh um numero inteiro nao negativo.
    '''

    k_fat = 1

    while k > 1:
        k_fat = k_fat * k
        k = k -1  

    return k_fat


def combinacao(m, n):
    '''(int, int) -> int
    Recebe dois inteiros m e n, e retorna o valor de m!/((m-n)! n!)
    '''


    return fatorial(m)//(fatorial(m-n)*fatorial(n))

main()
