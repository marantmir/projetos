import turtle

def desenhaQuadrado(t, tam):
    """Faca a tartaruga t desenhar um quadrado de lado tam."""

    for i in range(4):
        t.forward(tam)
        t.left(90)


wn = turtle.Screen()              # Inicializa a janela e seus atributos
wn.bgcolor("lightgreen")

alex = turtle.Turtle()            # cria alex

alex.color("lightcoral")

alex.pensize(3)

for k in range(1,6):
    alex.up()
    alex.goto(-10*k,-10*k)
    alex.down()
    desenhaQuadrado(alex, 20*k)         # Chama a função para desenhar um quadrado

alex.up()    
alex.goto(-100,-100)    
    
wn.exitonclick()