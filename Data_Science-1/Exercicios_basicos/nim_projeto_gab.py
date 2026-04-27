def usuario_escolhe_jogada(n,m):

        usuario_jogada = int(input("\nQuantas peças você vai tirar? "))
        while usuario_jogada > m or usuario_jogada <= 0 or usuario_jogada > n:    
                print("Oops! Jogada inválida! Tente de novo.")
                usuario_jogada = int(input("\nQuantas peças você vai tirar? "))
        
        return usuario_jogada

def computador_escolhe_jogada(n,m):

        computador_jogada = 1
        while computador_jogada != m:
                if (n-computador_jogada) % (m+1) == 0:
                        return computador_jogada
                else:
                        computador_jogada += 1
        
        return computador_jogada
        
def partida():
        
    valido = True
    while valido == True:
        n = int(input('\nQuantas peças? '))
        m = int(input('Limite de peças por jogada? '))

        if n > 0 and m >0 and n >= m: 

         if n % (m+1) == 0:
                print('\nUsuario começa')
        

                partida_terminou = False
                while partida_terminou != True:

                        pc_jogou = True
                        while pc_jogou == True:
                                removidas_usuario = usuario_escolhe_jogada(n,m)
                                n = n - removidas_usuario
                                if removidas_usuario == 1 and n > 1:
                                        print(f'''\nVocê tirou uma peça.\nAgora restam {n} peças no tabuleiro.''')
                                
                                elif removidas_usuario == 1 and n == 1:
                                        print(f'''\nVocê tirou uma peça.\nAgora resta apenas uma peça no tabuleiro.''')

                                else:
                                        print(f'''\nVocê tirou {removidas_usuario} peças.\nAgora restam {n} peças no tabuleiro.''')
                                
                                pc_jogou = False
                                pc_joga = True
                
                        pc_joga = True
                        while pc_joga == True:
                                removidas_computador = computador_escolhe_jogada(n,m)
                                n = n - removidas_computador

                                if n == 0 and removidas_computador == 1:
                                        print('''\nComputador tirou uma peça.\nFim do jogo! O computador ganhou!''')
                                        pc_joga = False

                                elif n == 0:
                                        print(f'''\nComputador tirou {removidas_computador} peças.\nFim do jogo! O computador ganhou!''')
                                        pc_joga = False

                                elif removidas_computador ==1:
                                        print(f'''\nComputador tirou uma peça.\nAgora restam {n} peças no tabuleiro.''')
                                        pc_joga = False

                                else:
                                        print(f'''\nComputador tirou {removidas_computador} peças.\nAgora restam {n} peças no tabuleiro.''')
                                        pc_joga = False

                        pc_jogou = True
                        if n > 0:
                                partida_terminou = False
                                print('\nSua vez!')
                        else:
                                partida_terminou = True
                                valido = False

         else:        
                print("\nComputador começa!")

                partida_terminou = False
                while partida_terminou != True:

                        pc_joga = True
                        while pc_joga == True:
                                removidas_computador = computador_escolhe_jogada(n,m)
                                n = n - removidas_computador

                                if n == 0 and removidas_computador == 1:
                                        print('''\nComputador tirou uma peça.\nFim do jogo! O computador ganhou!''')
                                        pc_joga = False
                                        partida_terminou = True
                                elif n == 0:
                                        print(f'''\nComputador tirou {removidas_computador} peças.\nFim do jogo! O computador ganhou!''')
                                        pc_joga = False
                                        partida_terminou = True

                                elif removidas_computador == 1:
                                        print(f'''\nComputador tirou uma peça.\nAgora restam {n} peças no tabuleiro.''')
                                        pc_joga = False

                                else:
                                        print(f'''\nComputador tirou {removidas_computador} peças.\nAgora restam {n} peças no tabuleiro.''')
                                        pc_joga = False
                        
                        if n > 0:
                                print('Sua vez.')
                                pc_jogou = True
                                while pc_jogou == True:
                                        removidas_usuario = usuario_escolhe_jogada(n,m)
                                        n = n - removidas_usuario
                                        if removidas_usuario == 1 and n > 1:
                                                print(f'''\nVocê tirou uma peça.\nAgora restam {n} peças no tabuleiro.''')
                                
                                        elif removidas_usuario == 1 and n == 1:
                                                print(f'''\nVocê tirou uma peça.\nAgora resta apenas uma peça no tabuleiro.''')

                                        else: #Removidas usuario for maior que 1 e tem mais de uma peça no tabuleiro.
                                                print(f'''\nVocê tirou {removidas_usuario} peças.\nAgora restam {n} peças no tabuleiro.''')
                                
                                        pc_jogou = False
                                        pc_joga = True
                        
                        else:
                                partida_terminou = True
                                valido = False
        else:
            print("Opção invalida, repita.")

def campeonato():
        rodada = 1
        while rodada <= 3:
                print(f"\n**** Rodada {rodada} ****")
                partida()
                rodada+=1
        rodada -=1
        print(f'''\n**** Final do campeonato! ****\nPlacar: Você 0 x {rodada} Computador\n''')

def main():
 continuar = False
 while continuar == False:
   
        tipo_partida = input('''\nBem-vindo ao jogo do NIM! Escolha:
        1 - para jogar uma partida isolada
        2 - para jogar um campeonato ''').replace(' ', '')

        if tipo_partida == "1" or tipo_partida == "2" :
                continuar = True
                if tipo_partida == "1":
                        print("\nVocê escolheu partida isolada!")
                        partida()
                else:
                        print("\nVocê escolheu um campeonato!")
                        campeonato()

        else:
                continuar = False
                print("Digite uma opção válida")

main()