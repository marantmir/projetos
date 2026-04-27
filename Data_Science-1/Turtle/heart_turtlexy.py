x = [ round(x * 00.01, 1) for x in range(-99, 99)]

y = [(1-k**2)**(0.5)+k**(2/3) for k in x]
print(x,y)
