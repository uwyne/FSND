def chunker(iterable, size):
    """Yield successive chunks from iterable of length size."""
    listlocal = [*range(0, len(iterable), size)]
    print (listlocal)
    for i in range(0, len(iterable), size):
        print( *iterable[i:i + size])

#for chunk in chunker(range(25), 4):
#    print(list(chunk))

chunker(range(25), 4)
