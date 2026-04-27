def somaquad(n):
    s = 0
    for k in range(1,n+1):
        s+=k**2
    return s

if __name__ == "__main__":
    print(somaquad(12))
