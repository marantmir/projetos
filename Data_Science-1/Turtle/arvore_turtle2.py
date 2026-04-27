import turtle
import random as rnd

def tree(branchLen,t):
    if branchLen > 5:
        t.st()
        ang1 = rnd.randint(15,35)
        dec = 15
        
        t.forward(branchLen)
        t.right(ang1)
        t.forward(branchLen-dec)
        tree(branchLen-dec,t)
        t.backward(branchLen-dec)
        t.left(40)
        t.forward(branchLen-dec)
        tree(branchLen-dec,t)
        t.backward(branchLen-dec)        
        t.right(40-ang1)
        tree(branchLen-dec,t)
        t.backward(branchLen)
        t.pensize(branchLen/20)
        if branchLen < 25:
            t.color("green")
            t.shape("circle")
            t.shapesize(0.5)
            t.stamp()
            
        elif branchLen < 45:
            t.color("#FFDEAD")
        else:
            t.color("brown")
        t.ht()
	

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    t.left(90)
    t.up()
    t.backward(200)
    t.down()
    t.speed(20)
    t.color("green")
    tree(80,t)
    myWin.exitonclick()

main()
