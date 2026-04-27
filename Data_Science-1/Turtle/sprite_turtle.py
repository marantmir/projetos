import turtle

wn = turtle.Screen()
wn.bgcolor("#90ee90") #rgb 144 238 144
rafturtle = turtle.Turtle()

rafturtle.color("black")
rafturtle.pensize(3)

rafturtle.shape("triangule")


legs = int(input("How many legs do you want your sprite to have? "))

for k in range(legs):
    rafturtle.forward(110)
    rafturtle.forward(10)
    rafturtle.forward(30)
    rafturtle.stamp()
    rafturtle.forward(-150)
    rafturtle.right(360/legs)
    
rafturtle.shape("circle")