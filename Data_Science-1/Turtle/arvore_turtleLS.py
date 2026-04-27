import turtle

def tree(Nbranch,t):
    if Nbranch>1:
        ang1 = 22
        t.forward(2)
        t.right(2*ang1)
        tree(Nbranch-1,t)
        t.left(3*ang1)
        tree(Nbranch-1,t)
        t.right(ang1)
        t.backward(2)
                

def main():
    t = turtle.Turtle()
    myWin = turtle.Screen()
    t.color("green")
    n = int(input("Quantas iterações você deseja usar: "))
    myWin.setworldcoordinates(-n*5,0,n*5,n*25)
    t.left(90)
    tree(n,t)
    myWin.exitonclick()

main()
