from queue import Queue


if __name__ == '__main__':
    test = Queue()
    test.put(2)
    test.put(3)
    test.put(3)
    test.put(4)
    test.put(5)
    test.put(5)
    print(test.get())