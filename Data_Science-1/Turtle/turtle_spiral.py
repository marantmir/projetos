import turtle

def desenhaQuadrado2(t, tam):
    """Faca a tartaruga t desenhar um quadrado de lado tamanho inicial."""
    acum = tam
    for i in range(150):
        acum = acum + 2
        t.forward(acum)
        t.left(91)  

wn = turtle.Screen()              # Inicializa a janela e seus atributos
wn.bgcolor("lightgreen")

alex = turtle.Turtle()            # cria alex

alex.color("blue")        

alex.speed(0)

desenhaQuadrado2(alex, 2)