import math
import turtle

def drawpolig(t, r, n):
    """Make turtle t draw a circle of radius r."""
    
    alfa_r = 2*math.pi/n
    alfa_d = 360/n

    for i in range(n):
        fw = 2*r*math.sin(alfa_r/2)
        t.forward(fw)
        t.right(alfa_d)
        
print(math.pi)

t = turtle.Turtle()

drawpolig(t, 100, 30)