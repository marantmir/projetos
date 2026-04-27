def insertion_sort(arr):
  
    arr2 = arr[:]
    
    for i in range(1, len(arr2)):
  
        key = arr2[i]
        j = i-1
        while j >=0 and key < arr2[j] :
                arr2[j+1] = arr2[j]
                j -= 1
        arr2[j+1] = key
    return arr2
  
