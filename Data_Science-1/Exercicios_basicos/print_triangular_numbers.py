def triangular_numbers(n):
    cnt = 0
    for k in range(1,n+1):
        cnt = cnt + k
    return cnt

def print_triangular_numbers(n):
    for k in range(n+1):
        print(k,"\t",triangular_numbers(k))
        
