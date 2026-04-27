import turtle
import random as rnd

def tree(branchLen,t):
    if branchLen > 5:
	ang1 = rnd.randint(15,35)
	dec = rnd.randint(15,35)
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
        if branchLen < 35:
            t.color("green")
            
        elif branchLen < 45:
            t.color("#FFDEAD")
        else:
            t.color("brown")
	

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