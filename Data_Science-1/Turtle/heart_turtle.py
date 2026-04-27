import turtle

x = [ round(x * 0.01, 2) for x in range(-200, 201,4)]

y = [(1-(abs(k)-1)**2)**(1/2) for k in x]

x2 = [ round(x * 0.01, 2) for x in range(200, -201,-4)]

y2 = [-2.5*(1-(abs(k)/2))**(1/2) for k in x2]

t = turtle.Turtle()
myWin = turtle.Screen()
myWin.tracer(1)
t.speed('fastest')
t.up()
t.goto(-200,0)
t.down()
t.ht()
t.begin_fill()
t.color("red")

for k,j in zip(x,y):
    t.goto(k*100,j*100)

for k,j in zip(x2,y2):
    t.goto(k*100,j*100)
    
t.end_fill()
turtle.done()
turtle.exitonclick()
