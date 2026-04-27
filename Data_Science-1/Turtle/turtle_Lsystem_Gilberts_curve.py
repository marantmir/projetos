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
    if ch == 'L':
        newstr = '+RF-LFL-FR+'   # Rule 1

    elif ch == 'R':
        newstr = '-LF+RFR+FL-'   # Rule 2
    else:
        newstr = ch    # no rules apply so keep the character

    return newstr

def drawLsystem(aTurtle,instructions,angle,distance):
    for cmd in instructions:
        if cmd in 'LRF':
            aTurtle.forward(distance)
        elif cmd == 'B':
            aTurtle.backward(distance)
        elif cmd == '+':
            aTurtle.right(angle)
        elif cmd == '-':
            aTurtle.left(angle)
        else:
            print('Error:', cmd, 'is an unknown command')

def main():
    inst = createLSystem(5,"L")   #create the string
    t = turtle.Turtle()           #create the turtle
    wn = turtle.Screen()

    t.up()
    t.back(200)
    t.down()
    t.speed("fastest")
    drawLsystem(t,inst,90,5)      #draw the picture
                                  #angle 60, segment length 5
    wn.exitonclick()

main()
