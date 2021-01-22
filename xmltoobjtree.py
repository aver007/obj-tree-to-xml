


def get_A():
    class A(object):
        ARG = 1
    return A

A = get_A()
B = get_A()