import turtle
import random

def tree(branchLen,t):
    if branchLen > 5:
        t.pensize(branchLen/10)
        t.forward(branchLen)
        
        ang = random.randint(18,35)
        dec1 = random.randint(1,20)
        dec2 = random.randint(1,20)
        
        t.right(ang)
        tree(branchLen-dec1,t)
        t.left(2*ang)
        tree(branchLen-dec2,t)
        t.right(ang)
        t.backward(branchLen)
        
                
        if branchLen < 10:        
            t.color("green")
        else:
            t.color("brown") 
        t.ht()

def main():
    t = turtle.Turtle()   
    myWin = turtle.Screen()
    myWin.tracer(100)
    t.left(90)
    t.up()
    t.backward(100)
    t.down()
    t.color("brown")
    t.speed(10)
    tree(100,t)
    myWin.exitonclick()

main()
