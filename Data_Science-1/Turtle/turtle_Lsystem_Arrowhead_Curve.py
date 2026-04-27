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
    if ch == 'X':
        newstr = 'YF+XF+Y'   # Rule 1

    elif ch == 'Y':
        newstr = 'XF-YF-X'   # Rule 2
    else:
        newstr = ch    # no rules apply so keep the character

    return newstr

def drawLsystem(aTurtle,instructions,angle,distance):
    saved_states = []
    head_states = []
    for cmd in instructions:
        if cmd in 'F':
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
        #else:
            #print('Error:', cmd, 'is an unknown command')

def main():
    inst = createLSystem(5,"YF")   #create the string
    t = turtle.Turtle()           #create the turtle
    wn = turtle.Screen()

    #wn.tracer(100)
    wn.setworldcoordinates(-500,-200,500,800)
    #t.up()

    #t.left(90)
    t.down()
    t.speed("fastest")
    t.ht()
    drawLsystem(t,inst,60,5)      #draw the picture
   
    wn.exitonclick()

main()
