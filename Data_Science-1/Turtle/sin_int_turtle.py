import turtle
import math


t = turtle.Turtle()
myWin = turtle.Screen()

myWin.tracer(100)

myWin.setworldcoordinates(0,-1.1,1000,1.1)

t.up()
t.speed("fastest")

for k in range(1000):
    t.dot()
    t.goto(k,math.sin(k))

myWin.exitonclick()

main()
