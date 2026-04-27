import random
import turtle

def isInScreen(w,t):
    leftBound = - w.window_width() / 2
    rightBound = w.window_width() / 2
    topBound = w.window_height() / 2
    bottomBound = -w.window_height() / 2

    turtleX = t.xcor()
    turtleY = t.ycor()

    stillIn = True
    if turtleX > rightBound or turtleX < leftBound:
        stillIn = False
    if turtleY > topBound or turtleY < bottomBound:
        stillIn = False

    return stillIn

t1 = turtle.Turtle()
wn = turtle.Screen()

t1.shape('turtle')

t2 = t1.clone()

leftBound = - wn.window_width() // 4
rightBound = wn.window_width() // 4
topBound = wn.window_height() //4
bottomBound = -wn.window_height() // 4

x1 = random.randint(leftBound,rightBound)
y1 = random.randint(bottomBound,topBound)

x2 = random.randint(leftBound,rightBound)
y2 = random.randint(bottomBound,topBound)

t1.up()
t2.up()
t1.goto(x1,y1)
t2.goto(x2,y2)
t1.down()
t2.down()

while isInScreen(wn,t1):
    coin = random.randrange(0, 2)
    if coin == 0:
        t1.left(random.randint(0,90))
        t2.left(random.randint(0,90))
    else:
        t1.right(random.randint(0,90))
        t2.right(random.randint(0,90))

    t1.forward(random.randint(0,50))
    t2.forward(random.randint(0,50))
    if t1.distance(t2) < 0.1:
        t2.right(180)

  

wn.exitonclick()



