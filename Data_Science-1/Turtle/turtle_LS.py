import turtle

def turtlecmd(t,turtle_program, turn_amount=45,step = 1):
    saved_states = []
    head_states = []
    for command in turtle_program:
        if command in "ABCDEFGHIJXY":
            t.down()
            t.fd(step)
        elif command == "abcdefghij":
            t.up()
            t.fd(step)
        elif command == '+':     # Turn turtle clockwise without moving
            t.down()
            t.right(turn_amount)
            
        elif command == '-':     # Turn turtle counter-clockwise without moving
            t.down()
            t.left(turn_amount)
            
        elif command == '[':                       # Remember current state
            saved_states.append(t.pos())
            head_states.append(t.heading())

        elif command == ']':                       # Return to previous state
            state = saved_states.pop()
            t.up()
            t.goto(state)
            t.setheading(head_states.pop())
            t.down()
            
def transform_sequence(sequence, transformations):
    return ''.join(transformations.get(c, c) for c in sequence)


def transform_multiple(sequence, transformations, iterations):
    for _ in range(iterations):
        sequence = transform_sequence(sequence, transformations)
    return sequence



