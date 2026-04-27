#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
x1 = int(input('Insira o valor da primeira abcissa :'))
y1 = int(input('Insira o valor da primeira ordenada:'))
x2 = int(input('Insira o valor da segunda abcissa :'))
y2 = int(input('Insira o valor da segunda ordenada:'))

d = math.sqrt((x2-x1)**2+(y2-y1)**2)

if d >= 10:
    print("longe")
else:
    print("perto")

