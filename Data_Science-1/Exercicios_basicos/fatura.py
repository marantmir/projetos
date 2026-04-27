#!/usr/bin/env python
# coding: utf-8

# In[37]:


name = input('Digite o nome do cliente:')
venc_d = int(input('Digite o dia de vencimento:'))
venc_m = input('Digite o mês de vencimento:')
val = input('Digite o valor da fatura:')
print(f'Olá, {name}\nA sua fatura com vencimento em {venc_d} de {venc_m} no valor de R$ {val} está fechada.')

