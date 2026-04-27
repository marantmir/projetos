def main():
    print("Bem-vindo ao jogo do NIM! Escolha:")
    n = int(input(
        "1 - para jogar uma partida isolada \n2 - para jogar um campeonato "))

    if n == 2:
        print("Voce escolheu um campeonato!")
    else:
        print("Voce escolheu uma partida isolada!")
        
main()

