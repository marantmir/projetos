limit=int(input("Enter upper limit:"))
c=0
m=2

# Este método não contempla todas as ternas possíveis
while(c<limit):
    for n in range(1,m+1):
        a=m*m-n*n
        b=2*m*n
        c=m*m+n*n
        if(c>limit):
            break
        if(a==0 or b==0 or c==0):
            break
        al.append(a)
        bl.append(b)
        cl.append(c)
    m=m+1

    
for j in cl2:
    for i in range(1,j):
        if (j**2-i**2)**0.5 - round((j**2-i**2)**0.5,0) == 0:
            print(i,"e ",(j**2-i**2)**0.5," formam a terna com",j)
