import turtle
from math import *
from tractrix import tract1, tract0


curva = 180

# Dados do Cavalo
lfrontal = 2.49 #   Largura frontal
eixof = 0.91 # Recuo do eixo em relação a frente do veículo
d_eixo = 4 # Distância entre eixos
ltraseira = 2.49 #   Largura traseira
eixot = 0.91 # Recuo do eixo em relação a frente do veículo

alfa = 25 # ângulo máximo de esterçamento : alfa (Graus)
dx = 1 # Discretização, indicando o acrescimo de posição a cada iteração
rmin = d_eixo / sin(radians(alfa)) # Raio mínimo da composição
teta = degrees(2*asin(dx/(2*rmin)))# Angulo de giro pata a trajetória circular de menor raio definida

t = turtle.Turtle()
wn = turtle.Screen()
wn.setworldcoordinates(-10,-5, 50,55)

# Eixos e extremidades do cavalo

t2 = t.clone() # Roda dianteira direita
t2.up()
t2.goto(eixof,lfrontal/2)


t3 = t.clone() # Roda dianteira esquerda
t3.up()
t3.goto(eixof,-lfrontal/2)

t4 = t.clone() # Eixo traseiro
t4.up()
t4.goto(-d_eixo,0)
d14 = -t4.xcor() # Distância entre t1(t) e t4

t5 = t.clone() # Lateral traseira direita
t5.up()
t5.goto(-d_eixo-eixot,-ltraseira/2)


t6 = t.clone() # Lateral traseira esquerda
t6.up()
t6.goto(-d_eixo-eixot,ltraseira/2)


colors = ["black","green","green"]*3


for k,j in zip([t,t2,t3,t4,t5,t6],colors):
    k.color(j)
    k.speed("fastest")
    k.down()


for _ in range(10):
    for k in [t,t2,t3,t4,t5,t6]:
        k.fd(dx)


alfa2 = 0
while t.heading() <= curva:
    if alfa2 < teta :
        alfa2 = alfa2+0.1
    else:
        alfa2 = teta
 
    t.lt(alfa2)
    t.fd(dx)
    tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)

delta_head = t.heading()- curva

while delta_head > 0.1:
    delta_head = t.heading()- curva
    t.setheading(curva + 0.9*delta_head)
    t.fd(dx)
    tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)
 

for _ in range(10):
    t.setheading(curva)
    t.fd(dx)
    tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)
