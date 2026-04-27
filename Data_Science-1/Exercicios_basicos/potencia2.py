n = int(input("Digite um inteiro para a base: "))
k = int(input("Digite um inteiro para o expoente: "))

mult = 1
sum = 0

while sum != k:
    mult = mult*n
    sum = sum +1
    
print(n,"elevado a",k,"é igual a",mult)
