#!/usr/bin/env python
# coding: utf-8

# In[5]:


import math
a = int(input('Insira o valor de a:'))
b = int(input('Insira o valor de b:'))
c = int(input('Insira o valor de c:'))

d = b**2 -4*a*c

if d == 0:
    print("a raiz desta equação é",-b/(2*a))
else:
    if d < 0:
        print("esta equação não possui raízes reais")
    else:
        r1 = (-b - math.sqrt(d))/(2*a)
        r2 = (-b + math.sqrt(d))/(2*a)
        print("as raízes da equação são",r1,"e",r2)

