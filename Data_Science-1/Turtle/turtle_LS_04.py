import turtle
#import turtle_LS
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

t.speed("fastest")
wn.setworldcoordinates(-50,0,50,100)
wn.tracer(100)

t.left(90)
t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('A', {'F': 'FF', 'A': 'F[-AF+[A]][++A][+++A]'}, 5),22.5)
