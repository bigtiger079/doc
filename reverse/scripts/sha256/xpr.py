# -- coding: utf-8 --
class XprInterface():
    def __init__(self, xpr, rxpr, param=[]):
        self.xpr = xpr
        self.revert_xpr = rxpr
        self.result = None

    def setArg(self, arg):
        self.result = self.revert_xpr(arg)

    def getResult(self):
        return self.xpr(self.result)


def rotate_left(a, k):
    k = k % 32
    return ((a << k) & 0xFFFFFFFF) | ((a & 0xFFFFFFFF) >> (32 - k))


def rotate_right(a, k):
    k = k % 32
    return ((a >> k) & 0xFFFFFFFF) | ((a & 0xFFFFFFFF) << (32 - k))


def right_shift(a, k):
    k = k % 32
    return (a & 0xFFFFFFFF) >> k


def left_shift(a, k):
    k = k % 32
    return ((a << k) & 0xFFFFFFFF)


# def revertFuncSSIG0(x):

express = [
    XprInterface(xpr=lambda x: x, rxpr=lambda x:x),
    # XprInterface(xpr=lambda x: (rotate_right(args[0] + x, 7)) ^ (rotate_right(args[0] + x, 18)) ^ (rotate_shift(args[0] + x, 3)))
]
