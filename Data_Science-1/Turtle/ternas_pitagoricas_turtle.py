import turtle

limit=int(input("Enter upper limit:"))


t = turtle.Turtle()
wn = turtle.Screen()
wn.setworldcoordinates(0,0,limit,limit)
wn.tracer(100)

t.up()
t.speed('fastest')

t2 = t.clone()

       
t3 = t.clone()
t3.color("blue")


# Este método contemnpla todas as ternas possíveis
for j in range(2,limit):
    for i in range(1,j):
        if (j**2-i**2)**0.5 == int((j**2-i**2)**0.5):
            t3.dot()
            t3.goto(i,(j**2-i**2)**0.5)        

# Este método não contemnpla todas as ternas possíveis
c=0
m=2
while(c<limit):
    for n in range(1,m+1):
        a=m*m-n*n
        b=2*m*n
        c=m*m+n*n
        if(c>limit):
            break
        if(a==0 or b==0 or c==0):
            break
        t.dot()
        t.goto(a,b)
        t2.dot()
        t2.goto(b,a)
    m=m+1

t.ht()
t2.ht()
t3.ht()
