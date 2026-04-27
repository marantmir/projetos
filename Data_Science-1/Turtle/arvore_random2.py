import turtle
import random

def tree(branchLen,t):
    if branchLen > 5:
        t.forward(branchLen)
        
        ang = random.randint(10,30)
        dec = random.randint(12,18)
        
        t.right(ang)
        t.forward(branchLen-dec)
        tree(branchLen-dec,t)
        t.backward(branchLen-dec)
        t.left(2*ang)
        t.forward(branchLen-dec)
        tree(branchLen-dec,t)
        t.backward(branchLen-dec)
        t.right(ang)
        tree(branchLen-dec,t)
        t.forward(-branchLen)

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    myWin.tracer(100)
    t.left(90)
    t.up()
    t.ht()
    t.backward(200)
    t.down()
    t.color("green")
    t.right(30)
    for k in range(1,4):
        t.left(k*10)
        tree(65,t)
    myWin.exitonclick()

main()
