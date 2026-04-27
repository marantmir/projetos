
import turtle
#import turtle_LS
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

#t.speed("fastest")

l = 30

wn.setworldcoordinates(-l,-l,l,l)
wn.tracer(10)


t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('FA', {'F': '+F+F+[F+F+F+F]++'}, 4),60)
