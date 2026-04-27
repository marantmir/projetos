import math

class bhaskara:
    '''
    Faz os calculos da formula de bascara e retorna os valores, 
    esse código foi refatorado para ser orientado a objetos e facilitar os testes.
    '''

    def main(self):

        a = float(input("Digite o valor de a: "))
        b = float(input("Digite o valor de b: "))
        c = float(input("Digite o valor de c: "))
    
    def delta(self, a, b, c):
        return b ** 2  - 4 * a *c
        
    def calcula(self, a, b, c):
        d = self.delta(a,b,c)

        if d < 0:
            return 0

        elif d  == 0:
            return 1, -b / (2*a)

        elif d > 0:
            result_1 = (-b + math.sqrt(d)) / (2*a)
            result_2 = (-b - math.sqrt(d)) / (2*a)
            return 2, result_1, result_2

        else:
            print("Ocorreu um erro inexperado, verifique o código!")
