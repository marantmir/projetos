class Ordenador:
    
    def selecao_direta(self,lista):
        fim = len(lista)
        for k in range(fim-1):
            for j in range(k+1,fim):
                if lista[j] < lista[k]:
                    lista[k],lista[j] = lista[j],lista[k]   
                    
    def bolha(self,lista):
        fim = len(lista)
        for i in range(fim-1,0,-1):
            trocou = False # Verifica se a lista já esta ordenada.
            for j in range(i):
                if lista[j] > lista[j+1]:
                    lista[j],lista[j+1] = lista[j+1],lista[j]
                    trocou = True
            if not trocou:
                return
