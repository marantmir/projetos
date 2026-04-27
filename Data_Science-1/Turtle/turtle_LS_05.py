import turtle
#import turtle_LS
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

t.speed("fastest")

l = 10

wn.setworldcoordinates(-l,-l,l,l)
wn.tracer(1)

t.left(90)
t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('F', {'F': '--F+F'}, 7),30)
