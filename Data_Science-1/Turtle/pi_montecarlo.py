import turtle
import math
import random

fred = turtle.Turtle()

wn = turtle.Screen()
wn.setworldcoordinates(-1,-1,1,1)
wn.tracer(100)

turtle.goto(0,-1)
turtle.circle(1)

fred.up()
fred.speed(speed = 0)

numdarts = 10000
count_in = 0

for i in range(numdarts):
    randx = random.random()
    randy = random.random()

    x = -1 + 2*randx
    y = -1 + 2*randy
    fred.stamp()
    fred.goto(x,y)
    if fred.distance(0,0) <= 1:
        fred.color("blue")
        count_in = count_in + 1 
    else:
        fred.color("red")
        
print(100*count_in/numdarts,"% dos pontos foram detro do círculo")
print(4*count_in/numdarts,"é o valor aproximado de pi")
        
wn.exitonclick()