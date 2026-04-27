import turtle

def drawBar(t, height):
    """ Get turtle t to draw one bar, of height. """
    if height >= 200:
        t.fillcolor("red")
    elif 100 <=height < 200:
        t.fillcolor("yellow")
    else:
        t.fillcolor("green")    
    
    t.begin_fill()               # start filling this shape
    t.left(90)
    t.forward(height)
    t.right(90)
    t.forward(40)
    t.right(90)
    t.forward(height)
    t.end_fill()                 # stop filling this shape
    
    t.up()
    
    if height > 0:
        head1 = height + 5
    else:
        head1 = height - 10
        
    t.goto(t.xcor()-27.5, head1)
    t.write(str(height))
    t.goto(t.xcor()+27.5, 0)
    t.left(90)
    t.down()
    
xs = [48, 117, 200, 240, 160, 260, 220,-60]  # here is the data
maxheight = max(xs)

minheight = 0
if min(xs)<0:
    minheight = min(xs)
    
numbars = len(xs)
border = 25

wn = turtle.Screen()             # Set up the window and its attributes
wn.setworldcoordinates(-border, -border+minheight, 40*numbars+border, maxheight+border)
wn.bgcolor("lightgreen")

tess = turtle.Turtle()           # create tess and set some attributes
tess.color("blue")

tess.pensize(3)
tess.speed(10)


for a in xs:
    drawBar(tess, a)

tess.up()    
tess.goto(20*numbars,-10)

tess.ht()
tess.fillcolor("black")
tess.write("Gráfico de Barra com a Tartatuga",align="center")
   
    
wn.exitonclick()
