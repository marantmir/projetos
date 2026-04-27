n = int(input("Digite o tamanho da sequência:"))
npar = 0
k = 0
while k < n:
    num = int(input("Digite um número da sequência:"))
    k = k + 1
    if num % 2 == 0:
        npar = npar +1
        
print("Existem",npar,"números pares")
print("Existem",n - npar,"números impares")
