import turtle

def tree(branchLen,t):
    if branchLen > 5:
        t.forward(branchLen)
        t.right(20)
        tree(branchLen-15,t)
        t.left(40)
        tree(branchLen-15,t)
        t.right(20)
        t.backward(branchLen)

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    myWin.setworldcoordinates(-1000,-10,1000,1990)
    myWin.tracer(100)
    t.left(90)
    t.up()
    t.backward(100)
    t.down()
    t.color("green")
    t.speed('fastest')
    tree(200,t)
    myWin.exitonclick()

main()
