import turtle

def createLSystem(numIters,axiom):
    startString = axiom
    endString = ""
    for i in range(numIters):
        endString = processString(startString)
        startString = endString
        

    return endString

def processString(oldStr):
    newstr = ""
    for ch in oldStr:
        newstr = newstr + applyRules(ch)

    return newstr

def applyRules(ch):
    newstr = ""
    if ch == 'F':
        newstr = 'FF+[+F-F-F]-[-F+F+F]'   # Rule 1

    elif ch == 'Y':
        newstr = 'YFX[+Y][-Y]'   # Rule 2
    else:
        newstr = ch    # no rules apply so keep the character

    return newstr

def drawLsystem(aTurtle,instructions,angle,distance):
    saved_states = []
    head_states = []
    for cmd in instructions:
        if cmd in 'XYF':
            aTurtle.forward(distance)
        elif cmd == 'B':
            aTurtle.backward(distance)
        elif cmd == '+':
            aTurtle.right(angle)
        elif cmd == '-':
            aTurtle.left(angle)
        elif cmd == '[':
            saved_states.append(aTurtle.pos())
            head_states.append(aTurtle.heading())
        elif cmd == ']':
            state = saved_states.pop()
            aTurtle.goto(state)
            aTurtle.setheading(head_states.pop())
        else:
            print('Error:', cmd, 'is an unknown command')

def main():
    inst = createLSystem(4,"F")   #create the string
    t = turtle.Turtle()           #create the turtle
    wn = turtle.Screen()

    wn.tracer(100)
    wn.setworldcoordinates(-200,0,200,400)
    t.up()

    t.left(90)
    t.down()
    t.speed("fastest")
    t.ht()
    drawLsystem(t,inst,180/7,5)      #draw the picture
                                  #angle 60, segment length 5
    wn.exitonclick()

main()
