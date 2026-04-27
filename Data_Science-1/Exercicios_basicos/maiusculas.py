def maiusculas(s):
    st = ""
    for k in s:
        if ord(k) >= 65 and ord(k) <= 90:
            st = st + k
    return st
