import turtle

def desenhaQuadrado(t, tam):
    """Faca a tartaruga t desenhar um quadrado de lado tam."""

    for i in range(4):
        t.forward(tam)
        t.left(90)  


wn = turtle.Screen()              # Inicializa a janela e seus atributos
wn.bgcolor("lightgreen")

alex = turtle.Turtle()            # cria alex

alex.color("blue")

alex.pensize(1)
    
alex.speed(0)
    
for k in range(20):
    desenhaQuadrado(alex, 100)
    alex.right(18)

wn.exitonclick()