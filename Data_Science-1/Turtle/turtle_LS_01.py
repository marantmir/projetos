import turtle
#import turtle_LS
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

t.speed("fastest")
wn.setworldcoordinates(-150,-150,50,50)
wn.tracer(100)

t.left(90)
t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('F', {'F': '+F+F--F+F'}, 5))
