#!/usr/bin/env python
# coding: utf-8

# In[39]:


seg = int(input('Por favor, entre com o número de segundos que deseja converter:'))
seg2 = seg%60
minutos = seg//60
minutos2 = minutos%60
horas = minutos//60
horas2 = horas%24
dias = horas//(24)
print(f'{dias} dias, {horas2} horas, {minutos2} minutos e {seg2} segundos.')

