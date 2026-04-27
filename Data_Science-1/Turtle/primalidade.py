n = int(input("Digite um número inteiro: "))

div = 0
k = 2

while k <= int(n**0.5)+1:
    
    if n % k == 0:
        div = div + 1
    k+= 1
                  
if div == 0:
    print("primo")
else:
    print("não primo")