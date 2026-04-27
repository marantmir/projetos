n = int(input("Digite um número inteiro: "))

k = n
w = n % 10
adj = 0

while k > 0:
    k = k // 10
    if w == k % 10:
        adj = adj +1
        print("sim")
    w = k % 10
    
if adj == 0:
    print("não")