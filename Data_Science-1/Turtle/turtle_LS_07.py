import turtle
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

t.speed("fastest")
wn.tracer(100)

l = 150

wn.setworldcoordinates(-l,-l,l,l)

t.left(90)
t.up()
t.bk(l-10)
t.down()

t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('F', {'F': 'F[-F]F[+F]F'}, 5),25)
