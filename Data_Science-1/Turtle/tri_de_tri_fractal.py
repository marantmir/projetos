import turtle

myTurtle = turtle.Turtle()
myTurtle.speed('fastest')
myWin = turtle.Screen()

def desenha_montanha(myTurtle, lineLen,grau):
    if grau > 0:
        coord = (0,0)
        for k in range(grau):
            myTurtle.setheading(0)
            myTurtle.left(60)
            myTurtle.forward(lineLen)
            if k == 0:
                coord = myTurtle.pos()
            myTurtle.right(120)
            myTurtle.forward(lineLen)
        myTurtle.up()
        myTurtle.goto(coord)
        myTurtle.down()
        desenha_montanha(myTurtle, lineLen,grau-1)


desenha_montanha(myTurtle,10,15)
myWin.exitonclick()
