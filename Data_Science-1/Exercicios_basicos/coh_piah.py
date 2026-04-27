import re

def le_assinatura():
    '''A funcao le os valores dos tracos linguisticos do modelo e devolve uma assinatura a ser comparada com os textos fornecidos'''
    print("Bem-vindo ao detector automático de COH-PIAH.")
    print("Informe a assinatura típica de um aluno infectado:\n")

    wal = float(input("Entre o tamanho médio de palavra: "))
    ttr = float(input("Entre a relação Type-Token: "))
    hlr = float(input("Entre a Razão Hapax Legomana: "))
    sal = float(input("Entre o tamanho médio de sentença: "))
    sac = float(input("Entre a complexidade média da sentença: "))
    pal = float(input("Entre o tamanho medio de frase: "))

    return [wal, ttr, hlr, sal, sac, pal]

def le_textos():
    '''A funcao le todos os textos a serem comparados e devolve uma lista contendo cada texto como um elemento'''
    i = 1
    textos = []
    texto = input("Digite o texto " + str(i) +" (aperte enter para sair):")
    while texto:
        textos.append(texto)
        i += 1
        texto = input("Digite o texto " + str(i) +" (aperte enter para sair):")

    return textos

def separa_sentencas(texto):
    '''A funcao recebe um texto e devolve uma lista das sentencas dentro do texto'''
    sentencas = re.split(r'[.!?]+', texto)
    if sentencas[-1] == '':
        del sentencas[-1]
    return sentencas

def separa_frases(sentenca):
    '''A funcao recebe uma sentenca e devolve uma lista das frases dentro da sentenca'''
    return re.split(r'[,:;]+', sentenca)

def separa_palavras(frase):
    '''A funcao recebe uma frase e devolve uma lista das palavras dentro da frase'''
    return frase.split()

def n_palavras_unicas(lista_palavras):
    '''Essa funcao recebe uma lista de palavras e devolve o numero de palavras que aparecem uma unica vez'''
    freq = dict()
    unicas = 0
    for palavra in lista_palavras:
        p = palavra.lower()
        if p in freq:
            if freq[p] == 1:
                unicas -= 1
            freq[p] += 1
        else:
            freq[p] = 1
            unicas += 1

    return unicas

def n_palavras_diferentes(lista_palavras):
    '''Essa funcao recebe uma lista de palavras e devolve o numero de palavras diferentes utilizadas'''
    freq = dict()
    for palavra in lista_palavras:
        p = palavra.lower()
        if p in freq:
            freq[p] += 1
        else:
            freq[p] = 1

    return len(freq)

def compara_assinatura(as_a, as_b):
    '''Essa funcao recebe duas assinaturas de texto e deve devolver o grau de similaridade nas assinaturas.'''
    grau_similaridade = 0
    
    for k,j in zip(as_a,as_b):
        grau_similaridade = grau_similaridade + abs(k-j)/6
                             
    return grau_similaridade

def calcula_assinatura(texto):
    '''Essa funcao recebe um texto e deve devolver a assinatura do texto.'''
    sent = separa_sentencas(texto) # Sent é uma lista de sentenças
    
    frs_list = []
    for k in sent:
        frs_list.append(separa_frases(k))
    
    palav_list = []
    for k in frs_list:
        for j in k:
            palav_list.append(separa_palavras(j))
            
    def flatlist(lista):
        lst = []
        for k in lista:
            lst = lst + k
        return lst
    
    palav_list_plana = flatlist(palav_list.copy())
    frs_list_plana = flatlist(frs_list.copy())
    
    
    ##### Cálculo do tamanho médio das palavras em todo o texto #####
    soma0 = 0
    for k in palav_list_plana:
        soma0 = soma0 + len(k)
    tam_medio = soma0/len(palav_list_plana) # Tamanho médio das palavras
    ##################################################################
    
    ###### Relação Type-Token ########################################
    rel_type_token = n_palavras_diferentes(palav_list_plana)/len(palav_list_plana)
    ##################################################################
    
    ###### Razão Hapax Legomana #####################################
    rzao_hapax = n_palavras_unicas(palav_list_plana)/len(palav_list_plana)
    ##################################################################
    
    ###### Tamanho Médio da sentença #################################
    soma1 = 0
    for k in sent:
        soma1 = soma1 + len(k)
        
    tam_med_sentenca = soma1/len(sent)
    ##################################################################
    
    ###### Complexidade da Sentença ##################################
    comp_sentencias = len(frs_list_plana)/len(sent)
    ##################################################################
    
    ###### Tamanho médio de frase ####################################
    soma2 = 0
    for k in frs_list_plana:
        soma2 = soma2 + len(k)
    tam_med_frase = soma2/len(frs_list_plana)
    ##################################################################    
    
    
    return [tam_medio,rel_type_token,rzao_hapax,tam_med_sentenca,comp_sentencias,tam_med_frase]
    

def avalia_textos(textos, ass_cp):
    '''Essa funcao recebe uma lista de textos e uma assinatura ass_cp e deve devolver o numero (1 a n) do texto com maior probabilidade de ter sido infectado por COH-PIAH.'''
    
    sim_lista = []
    for k in textos:
        ass_k = calcula_assinatura(k)
        sim_k_mod = compara_assinatura(ass_cp, ass_k) 
        sim_lista.append(sim_k_mod)
    
    
    return sim_lista.index(min(sim_lista))+1


def main():
    
    ass_mod = le_assinatura() 
    
    lsttext = []
    txt_in = input("\nDigite o texto 1 (aperte enter para sair): ")
    
    cnt = 2
    
    while txt_in:
        lsttext.append(txt_in)
        txt_in = input(f"\nDigite o texto {cnt} (aperte enter para sair): ")
        cnt+=1
        
    print(f"\nO autor do texto {avalia_textos(lsttext, ass_mod)} está infectado com COH-PIAH")
