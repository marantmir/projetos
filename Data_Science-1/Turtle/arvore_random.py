import turtle
import random 

def tree(branchLen,t):
    if branchLen > 5:
        for k in range(1,4):
            j = 4 - k
            t.forward(k*branchLen/3)
            
            ang = random.randint(15,35)
            b = 10*random.random()
            c = 10*random.random()
            
            t.right(ang)
            t.forward(b+j*branchLen/6)
            tree(branchLen/6,t)            
            t.backward(b+j*branchLen/6)
            t.left(2*ang)
            t.forward(c+j*branchLen/6)
            tree(j*branchLen/6,t)
            t.backward(c+j*branchLen/6)
            t.right(ang)
            t.backward(k*branchLen/3)
            if branchLen <= 25 :
                t.color("green")
            else:
                t.color("brown")
        
def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    myWin.tracer(100)
    t.left(90)
    t.ht()
    t.up()
    t.backward(200)
    t.down()
    t.color("brown")
    tree(250,t)
    myWin.exitonclick()

main()