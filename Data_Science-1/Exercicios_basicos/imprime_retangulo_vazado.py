l = int(input("digite a largura: "))
a = int(input("digite a altura: "))
k = 0

while k < a:
    k+=1
    j = 0
    while j < l:
        j+=1
        if k in [1,a]:
            print("#",end="")
        else:
            if j in [1,l]:
                print("#",end="")
            else:
                print(" ",end="")
    print()
