import math
import turtle

rafturtle = turtle.Turtle()
wn = turtle.Screen()

wn.bgcolor("aquamarine")
rafturtle.shape("turtle")
rafturtle.color("blue")

rafturtle.pensize(2)

rafturtle.penup()
rafturtle.speed(8)
rafturtle.goto(-200, 0)
rafturtle.pendown()
rafturtle.lt(90)
rafturtle.forward(100)

rafturtle.right(90)
rafturtle.forward(25)

rafturtle.speed(12)
for k in range(18):
  rafturtle.right(10)
  rafturtle.forward(5)

rafturtle.forward(20)
rafturtle.left(135)
rafturtle.forward(65)

rafturtle.speed(8)
rafturtle.left(45)
rafturtle.penup()
rafturtle.forward(25)
rafturtle.pendown()

def escrever_a_f():
  #a
  rafturtle.setheading(90-18)
  rafturtle.forward(100)
  rafturtle.right(180-2*18)
  rafturtle.forward(100)
  rafturtle.forward(-50)
  rafturtle.setheading(180)
  rafturtle.forward(30)
  rafturtle.penup()
  rafturtle.setheading(0)
  rafturtle.forward(60)
  #f
  rafturtle.pendown()
  rafturtle.forward(30)
  rafturtle.forward(-30)
  rafturtle.rt(90)
  rafturtle.forward(50)
  rafturtle.forward(-100)
  rafturtle.right(90)
  rafturtle.forward(-60)


escrever_a_f()


rafturtle.penup()
rafturtle.left(90)
rafturtle.forward(100)

rafturtle.down()

# a e e
escrever_a_f()

rafturtle.up()
rafturtle.left(90)
rafturtle.forward(100)
rafturtle.right(90)
rafturtle.down()
rafturtle.forward(60)

#L
rafturtle.up()
rafturtle.backward(60+25+70)
rafturtle.down()
rafturtle.forward(50+25)
rafturtle.right(90)
rafturtle.forward(100)

rafturtle.up()
rafturtle.right(90)
rafturtle.goto(-210, -10)
rafturtle.color("#FF8C00")
rafturtle.down()
rafturtle.forward(450)


rafturtle.speed(13)
for k in range(1,100):
  rafturtle.goto(-200+(450/2)-((400)/k)*math.cos(k),-10 - 1.5*k)


rafturtle.color("black")
rafturtle.speed(5)
rafturtle.up()
rafturtle.goto(-200+(445/2), -200)
rafturtle.setheading(90)
rafturtle.write("Turtle Tricks", align="center", font=("Arial",25,"italic"))
rafturtle.forward(-30)
