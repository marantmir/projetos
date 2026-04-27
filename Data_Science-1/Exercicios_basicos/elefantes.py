def incomodam(n):
    if n < 1:
        return ""
    else:
        return "incomodam " + incomodam(n-1)


def elefantes(n):
    if n < 1:
        return ""
    
    if n == 2:
        return "Um elefante incomoda muita gente\n2 elefantes incomodam incomodam muito mais\n"
    else:
        return  elefantes(n-1)+f"{n-1} elefantes incomodam muita gente\n{n} elefantes {incomodam(n)}muito mais\n"
