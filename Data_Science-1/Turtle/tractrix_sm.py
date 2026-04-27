import turtle
from math import *
from tractrix import tract1, tract0


#curva = 180

wn = turtle.Screen()

wn.setworldcoordinates(-20,-5, 45,60)

#wn.tracer(100)

def trajetoria_sm(curva, dx):

    

    # Dados do Cavalo
    lfrontal = 2.49 #   Largura frontal
    eixof = 1.45 # Recuo do eixo em relação a frente do veículo
    d_eixo = 4.2 # Distância entre eixos
    ltraseira = 2.49 #   Largura traseira
    eixot = 0.71 # Recuo do eixo em relação a traseira do veículo

    # Dados do Reboque

    lrbq = 2.6 #Largura do reboque
    d4pr = -0.35 #Distância do eixo traseiro ao pino em m
    dp4er = 0 # Distância do pino rei ao primeiro eixo do reboque
    efr = 2.5 #Recuo do 1ºeixo (frontal) do reboque
    etr = 4.75 #Recuo do 2ºeixo (traseiro) do reboque
    dexr = 8.1 #Distância entre os eixos do reboque

    estsm = 15 # Angulo máximo de Esterçamento semi-reboque/CM (Graus)

    alfa = 25 #ângulo máximo de esterçamento : alfa (Graus)
    #dx = 0.5 # Discretização, indicando o acrescimo de posição a cada iteração
    rmin = d_eixo / sin(radians(alfa)) # Raio mínimo da composição
    teta = degrees(2*asin(dx/(2*rmin)))# Angulo de giro pata a trajetória circular de menor raio definida

    t = turtle.Turtle()


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


    t5 = t.clone() # Lateral traseira direita
    t5.up()
    t5.goto(-d_eixo-eixot,-ltraseira/2)


    t6 = t.clone() # Lateral traseira esquerda
    t6.up()
    t6.goto(-d_eixo-eixot,ltraseira/2)


    ## Eixos e extremidades do reboque ##

    t7 = t.clone() # Eixo frontal do reboque
    t7.up()
    t7.goto(t4.xcor()-(d4pr+dp4er),0)


    t8 = t.clone() # Extremidade esquerda forntal do reboque
    t8.up()
    t8.goto(t7.xcor()+efr,+lrbq/2)

    t9 = t.clone() # Extremidade direita forntal do reboque
    t9.up()
    t9.goto(t8.xcor(),-lrbq/2)

    t10 = t.clone() # Eixo traseiro do reboque
    t10.up()
    t10.goto(t7.xcor()-dexr,0)
    d710 = dexr

    t11 = t.clone() # Lateral traseira esquerda
    t11.up()
    t11.goto(t10.xcor()-etr,-lrbq/2)

    t12 = t.clone() # Lateral traseira direita
    t12.up()
    t12.goto(t11.xcor(),+lrbq/2)


    d14 = -t4.xcor() # Distância entre t1(t) e t4
    d47 = d4pr+dp4er
    d4_10 =  t4.xcor() - t10.xcor() # Distância entre t4 e t10


    #Menor distância permitida entre os pontos 1 e 10 com esterçamento máximo do semireboque
    md110 = (d14**2 + d4_10**2 + 2*d14*d4_10*cos(radians(estsm)))**(1/2)


    colors = ["black","green","green","black","red","red"]*2
    c = 0


    for k,j in zip([t,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12],colors):
        k.color(j)
        k.speed("fastest")
        k.down()
        k.begin_poly()

    t7.up()
    t7.ht()
    

    alfa2 = 0.1*teta
    while t.heading() <= curva - teta:
        if t.distance(t10) >= md110-dx: #Verificando o exterçamento máximo do Semireboque
            if alfa2 < teta :
                alfa2 = alfa2 + 0.1*teta
                t.lt(alfa2) 
            else:
                t.lt(teta)
            t.fd(dx)
        else:
            print("Semi reboque estercado, aumentar discretização 'dx'")
            print(t.distance(t10))
            t.fd(dx/20) # Se o semireboque estiver esterça, o veículo vai alinhar e depois girar
        
        tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)

        tract0(t4,t7,d47)    
        tract1(t7,t8,t9,t10,t11,t12,lrbq,efr,lrbq,etr,d710)
        

    delta_head = abs(curva - t.heading())

    print(t.heading())
    cnt = 0
    while delta_head > 0.01:
        cnt+=1
        t.lt(teta*0.1)
        t.fd(dx)
        tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)
        tract0(t4,t7,d47)    
        tract1(t7,t8,t9,t10,t11,t12,lrbq,efr,lrbq,etr,d710)
        print(t.heading())
        delta_head = curva - t.heading()

    for _ in range(10):
        t.setheading(curva)
        t.fd(dx)
        tract1(t,t2,t3,t4,t5,t6,lfrontal,eixof,ltraseira,eixot,d14)
        tract0(t4,t7,d47)    
        tract1(t7,t8,t9,t10,t11,t12,lrbq,efr,lrbq,etr,d710)


    lista_coord = []
    for k,j in zip([t,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12],colors):
        k.end_poly()
        lista_coord.append([[i,j] for i,j in k.get_poly()])

    c = 0
    for k in lista_coord:
        c+=1
        out = open('trajetoria_'+str(c)+'.scr', 'w')
        
        out.write('_PLINE')
        out.write('\n')
        
        for coord in k:
            out.write(f'{coord[0]:.4f},{coord[1]:.4f}')
            out.write('\n')


trajetoria_sm(90, 1)

wn.exitonclick()


