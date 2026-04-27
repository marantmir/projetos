n = 1
lista = []
while n != 0:
    n = int(input("Digite um número: "))
    lista.append(n)

comp = len(lista)
print()
for k in range(2,comp+1):
    print(lista[-k])
