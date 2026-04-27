import turtle
from math import *


def tract0(t,t4,d):
    
    xc, yc = t.pos()
    
    x_t4,y_t4 = t4.pos()

    if (xc - x_t4) != 0:
        
        a_rad = atan((yc - y_t4)/(xc - x_t4))
        a = degrees(a_rad)

        if abs(t.heading() - a) < abs(t.heading() -180 - a):
            a_rad = a_rad         
        else:
            a_rad =  pi + a_rad
            
    else:
        a_rad = pi/2
        a = degrees(a_rad)
    
    a = degrees(a_rad)
    t4.setheading(a)

    dx4 = t.distance(t4) - d
    
    t4.fd(dx4)


def tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14):
    '''Dado uma trajetória t, traça as demais trajetórias dos veículos t2,t3,t4,t5,t6'''
    
    tract0(t,t4,d14)

    xc, yc = t.pos()
    x_t4,y_t4 = t4.pos()
    
    for k in [t2,t3,t5,t6]:
        k.setheading(t4.heading())

    a_rad = radians(t4.heading())
    
    x_t2 = xc - (lfrontal/2)*sin(a_rad)+ eixof*cos(a_rad)
    y_t2 = yc + (lfrontal/2)*cos(a_rad)+ eixof*sin(a_rad)
    t2.goto(x_t2,y_t2)

    x_t3 = xc + (lfrontal/2)*sin(a_rad)+ eixof*cos(a_rad)
    y_t3 = yc - (lfrontal/2)*cos(a_rad)+ eixof*sin(a_rad)
    t3.goto(x_t3,y_t3)        

    x_t5 = x_t4 + (ltraseira/2)*sin(a_rad)- eixot*cos(a_rad)
    y_t5 = y_t4 - (ltraseira/2)*cos(a_rad)- eixot*sin(a_rad)
    t5.goto(x_t5,y_t5)    

    x_t6 = x_t4 - (ltraseira/2)*sin(a_rad)- eixot*cos(a_rad)
    y_t6 = y_t4 + (ltraseira/2)*cos(a_rad)- eixot*sin(a_rad)
    t6.goto(x_t6,y_t6)


if __name__ == "__main__":

    t = turtle.Turtle()


    wn = turtle.Screen()
    wn.setworldcoordinates(0,0,210,1200)
    wn.tracer(100)

    l = 200 #Comprimento da barra ligando t a t2

    t.pensize(4)
    t2 = t.clone()
    t2.up()
    t2.goto(l,0)
    t2.down()
    t3 = t2.clone()
    t3.pensize(2) 

    t.lt(90)
    t.speed("fastest")
    for _ in range(2*l):
        t.fd(l/50)
        tract0(t,t2,l)


    # Comparação entre a solução numérica e a analítica
    t3.color("Blue")
    x = l
    y = 0
    for k in range(l):
        x = l - k
        g = sqrt(l**2 - x**2)
        y = l*log(abs((l+g)/x)) - g
        t3.goto(x,y)


    wn.exitonclick()




