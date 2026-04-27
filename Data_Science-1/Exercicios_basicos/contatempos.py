import ordenador
import random
import time

class Contatempos:
    def lista_aleatoria(self,n):
        return [random.randrange(1000) for x in range(n)]
    
    def lista_quase_ordenada(self,n):
        lista = [x for x in range(n)]
        lista[n // 10] = -500
        return lista
    
    def compara(self,n):
        lista1 = self.lista_aleatoria(n)
        lista2 = lista1[:]
        
        o = ordenador.Ordenador()
        
        antes = time.time()
        o.bolha(lista1)
        depois = time.time()
        print("O algoritimo da bolha demorou", depois - antes, 'segundos')
        
        antes = time.time()
        o.selecao_direta(lista1)
        depois = time.time()
        print("O algoritimo selecao_direta", depois - antes, 'segundos')

        lista1 = self.lista_quase_ordenada(n)
        lista2 = lista1[:]
        
        o = ordenador.Ordenador()
        
        antes = time.time()
        o.bolha(lista1)
        depois = time.time()
        print("O algoritimo da bolha demorou", depois - antes, 'segundos')
        
        antes = time.time()
        o.selecao_direta(lista1)
        depois = time.time()
        print("O algoritimo selecao_direta", depois - antes, 'segundos')
