import turtle              # 1.  import the modules
import random
wn = turtle.Screen()       # 2.  Create a screen
wn.bgcolor('lightblue')

lance = turtle.Turtle()    # 3.  Create two turtles
andy = turtle.Turtle()
lance.color('red')
andy.color('blue')
lance.shape('turtle')
andy.shape('turtle')

andy.up()                  # 4.  Move the turtles to their starting point
lance.up()
andy.goto(-200,20)
lance.goto(-200,-20)

# your code goes here
xa = -200
ya = -200

xl = -200
yl = -200

while xa <= 200 and xl <=200:
    xa = xa + random.randint(1,10)
    xl = xl + random.randint(1,10)
    andy.goto(xa,20)
    lance.goto(xl,-20)

 
if xa > xl:
    winner = 'andy'
elif xa == xl:
    winner ='There is a tie' 
else:
    winner ='lance'
    
txtwin = winner+" is the winner!"


turtle.up()
turtle.goto(0,-120)
turtle.left(90)
turtle.write(txtwin,move=False, align ="center", font=("Arial", 12, "normal"))
turtle.backward(20)


wn.exitonclick()