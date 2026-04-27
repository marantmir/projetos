import turtle

def seq3np1(n):
    """
    Indica o número de iterações até a sequencia 3n+1
    até que a sequência convirja para 1.
    """
    count = 1
    while n != 1:
        count+=1
        if n % 2 == 0:        # n is even
            n = n // 2
        else:                 # n is odd
            n = n * 3 + 1
    return count                  # the last print is 1

t = turtle.Turtle()
wn = turtle.Screen()

wn.setworldcoordinates(0,0,50,150)

xmax = 0
maxSoFar = 0 

for k in range(1,50):
    seq = seq3np1(k)
    t.goto(k,seq)
    if seq > maxSoFar:
        maxSoFar = seq
        xmax = k
t.up()
t.goto(xmax,maxSoFar+5)
t.write("Maior valor "+str((xmax,maxSoFar)),align="center", font=("Arial", 8, "normal"))
t.goto(xmax,maxSoFar)
