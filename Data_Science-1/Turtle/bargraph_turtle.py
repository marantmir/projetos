import turtle

def drawBar(t, height):
    """ Get turtle t to draw one bar, of height. """
    t.begin_fill()               # start filling this shape
    t.left(90)
    t.forward(height)
    t.right(90)
    t.forward(40)
    t.right(90)
    t.forward(height)
    t.end_fill()                 # stop filling this shape
    t.speed(12)
    t.up()
    t.ht()
    t.forward(-height)
    t.left(90)
    t.backward(27.5)
    t.right(90)
    t.backward(5)
    t.write(str(height))
    t.forward(5)
    t.left(90)
    t.forward(27.5)
    t.right(90)
    t.forward(height)
    t.left(90)
    t.down()
    t.speed(4)
    t.st()
    
xs = [48, 117, 200, 240, 160, 260, 220]  # here is the data
maxheight = max(xs)
numbars = len(xs)
border = 25

wn = turtle.Screen()             # Set up the window and its attributes
wn.setworldcoordinates(-border, -border, 40*numbars+border, maxheight+border)
wn.bgcolor("lightgreen")

tess = turtle.Turtle()           # create tess and set some attributes
tess.color("blue")
tess.fillcolor("red")
tess.pensize(3)



for a in xs:
    drawBar(tess, a)

tess.up()    
tess.goto(20*numbars,-10)

tess.ht()
tess.fillcolor("black")
tess.write("Gráfico de Barra com a Tartatuga",align="center")
   
    
wn.exitonclick()