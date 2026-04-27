
import turtle
#import turtle_LS
from turtle_LS import turtlecmd, transform_multiple

t = turtle.Turtle()
wn = turtle.Screen()

t.speed("fastest")
wn.tracer(100)

l = 100

wn.setworldcoordinates(-l,-l,l,l)

t.left(90)
t.up()
t.bk(30)
t.down()

t.color("green")
t.pensize(3)

turtlecmd(t,transform_multiple('H', {'H': 'HFX[+H][-H]','X':'X[-FFF][+FFF]FX'}, 5),25.7)
