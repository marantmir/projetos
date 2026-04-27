import turtle
import random as rnd
from math import *


curva = 180

lfrontal = 2.49 #   Largura frontal
eixof = 0.91 # Recuo do eixo em relação a frente do veículo
d_eixo = 9 # Distância entre eixos
ltraseira = 2.49 #   Largura traseira
eixot = 0.91 # Recuo do eixo em relação a frente do veículo

alfa = 25 #ângulo máximo de esterçamento : alfa (Graus)
dx = 0.1 #Discretização, indicando o acrescimo de posição a cada iteração


t = turtle.Turtle()

wn = turtle.Screen()

wn.setworldcoordinates(-50,-50, 100,100)


t2 = t.clone() # Roda dianteira direita
t2.up()
t2.goto(eixof,lfrontal/2)


t3 = t.clone() # Roda dianteira esquerda
t3.up()
t3.goto(eixof,-lfrontal/2)
t3.down()

t4 = t.clone() # Eixo traseiro
t4.up()
t4.goto(-d_eixo,0)


t5 = t.clone() # Lateral traseira direita
t5.up()
t5.goto(-d_eixo-eixot-eixot,-ltraseira/2)


t6 = t.clone() # Lateral traseira esquerda
t6.up()
t6.goto(-d_eixo-eixot-eixot,ltraseira/2)


colors = ["black","green","green","black","red","red"]
c = 0

for k in [t,t2,t3,t4,t5,t6]:
    k.color(colors[c])
    c = c + 1
    k.speed("fastest")
    k.down()
    

for _ in range(10):
    for k in [t,t2,t3,t4,t5,t6]:
        k.fd(2)



alfa2 = 0
k = 0
a = 92
b = a



while t.heading() <= curva - alfa:
    a = t.heading()
    alfa2 = alfa2+0.1 if alfa2<alfa else alfa
    t.lt(alfa2)
    t.fd(1)
    
    b = t.heading()
    b_rad = radians(b)

    xc = t.xcor()
    yc = t.ycor()

    x_t2 = xc - (lfrontal/2)*sin(b_rad)+ eixof*cos(b_rad)
    y_t2 = yc + (lfrontal/2)*cos(b_rad)+ eixof*sin(b_rad)
    t2.setheading(b)
    t2.goto(x_t2,y_t2)

    x_t3 = xc + (lfrontal/2)*sin(b_rad)+ eixof*cos(b_rad)
    y_t3 = yc - (lfrontal/2)*cos(b_rad)+ eixof*sin(b_rad)
    t3.setheading(b)
    t3.goto(x_t3,y_t3)


    a_rad = radians(a)
    x_t4 = xc- d_eixo*cos(a_rad)
    y_t4 = yc- d_eixo*sin(a_rad)
    t4.setheading(a)
    t4.goto(x_t4,y_t4)

    x_t5 = x_t4 + (ltraseira/2)*sin(a_rad)- eixot*cos(a_rad)
    y_t5 = y_t4 - (ltraseira/2)*cos(a_rad)- eixot*sin(a_rad)
    t5.setheading(a)
    t5.goto(x_t5,y_t5)    

    x_t6 = x_t4 - (ltraseira/2)*sin(a_rad)- eixot*cos(a_rad)
    y_t6 = y_t4 + (ltraseira/2)*cos(a_rad)- eixot*sin(a_rad)
    t6.setheading(a)
    t6.goto(x_t6,y_t6)




delta_hd = curva - t.heading()
print(delta_hd)

alf2 = alfa

while t.heading() <= curva:
    alf2 = alf2 - 0.2
    print(alf2)
    t.lt(alf2)
    t.fd(1)
    b = t.heading()
    b_rad = radians(b)

    xc = t.xcor()
    yc = t.ycor()

    x_t2 = xc - (lfrontal/2)*sin(b_rad)+ eixof*cos(b_rad)
    y_t2 = yc + (lfrontal/2)*cos(b_rad)+ eixof*sin(b_rad)
    t2.setheading(b)
    t2.goto(x_t2,y_t2)

    x_t3 = xc + (lfrontal/2)*sin(b_rad)+ eixof*cos(b_rad)
    y_t3 = yc - (lfrontal/2)*cos(b_rad)+ eixof*sin(b_rad)
    t3.setheading(b)
    t3.goto(x_t3,y_t3)

    x_t4 = xc - d_eixo*cos(b_rad)
    y_t4 = yc - d_eixo*sin(b_rad)
    t4.setheading(b)
    t4.goto(x_t4,y_t4)

    x_t5 = x_t4 + (ltraseira/2)*sin(b_rad)- eixot*cos(b_rad)
    y_t5 = y_t4 - (ltraseira/2)*cos(b_rad)- eixot*sin(b_rad)
    t5.setheading(b)
    t5.goto(x_t5,y_t5)    

    x_t6 = x_t4 - (ltraseira/2)*sin(b_rad)- eixot*cos(b_rad)
    y_t6 = y_t4 + (ltraseira/2)*cos(b_rad)- eixot*sin(b_rad)
    t6.setheading(b)
    t6.goto(x_t6,y_t6)
