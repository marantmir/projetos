import turtle

t = turtle.Turtle()
wn = turtle.Screen()

def ehprimo(n):
    cond = True
    for k in range(2,int(n**0.5)+1):
        if n % k == 0:
            cond = False
    return cond
        

for k in range(100):
    t.fd(k)
    t.rt(18)
    if ehprimo(k):
        t.dot()
