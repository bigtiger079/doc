# -- coding: utf-8 --
class DataXpr():

    def __init__(self, ltype, lm, param=[]):
        self.lm = lm
        self.ltype = ltype
        self.result = -1

    def setReslut(self, r):
        self.result = r

    def getX(self):
        if self.ltype == 0:
            return self.result
        elif self.ltype == 6:
            pass

    def getLm(self):
        return self.lm

    def getType(self):
        return self.ltype

    def __add__(self, xpr):
        return createLm(3, self.getLm(), xpr.getLm())


def createLm(ltype, *args):

    if ltype == 0:
        return DataXpr(ltype=ltype, lm=(lambda x: x))
    elif ltype == 1:
        return DataXpr(ltype=ltype, lm=(lambda x: (rotate_right(args[0] + x, 7)) ^ (rotate_right(args[0] + x, 18)) ^ (rotate_shift(args[0] + x, 3))))
    elif ltype == 2:
        return DataXpr(ltype=ltype, lm=(lambda x: ((rotate_right(args[0] + x, 17)) ^ (rotate_right(args[0] + x, 19)) ^ (rotate_shift(args[0] + x, 10)))))
    elif ltype == 3:
        return DataXpr(ltype=ltype, lm=(lambda x: args[0](x) + args[1](x)))
    elif ltype == 4:
        return DataXpr(ltype=ltype, lm=(lambda x: (((args[0](x) + args[1]) << args[2]) & 0xFFFFFFFF)))
    elif ltype == 5:
        return DataXpr(ltype=ltype, lm=(lambda x: (((args[0](x) + args[1]) >> args[2]) & 0xFFFFFFFF)))
    elif ltype == 6:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0](x) + args[1]) ^ args[2]))
    elif ltype == 7:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0](x) + args[1]) ^ (args[2](x) + args[3])))
    elif ltype == 8:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0](x) + args[1]) & args[2]))
    elif ltype == 9:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0](x) + args[1]) & args[2]))
    elif ltype == 10:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0](x) + args[1]) & (args[2](x) + args[3])))
    elif ltype == 11:
        return DataXpr(ltype=ltype, lm=(lambda x: ~(args[0](x) + args[1])))
    elif ltype == 12:
        return DataXpr(ltype=ltype, lm=(lambda x: (((args[0].rsh(x) & 0xFFFFFFFF) | (args[0].lsh(32 - x) & 0xFFFFFFFF)) & 0xFFFFFFFF)))
    elif ltype == 13:
        return DataXpr(ltype=ltype, lm=(lambda x: ((args[0].lsh(x) & 0xFFFFFFFF) | (args[0].rsh(32 - x) & 0xFFFFFFFF))))
    elif ltype == 14:
        return DataXpr(ltype=ltype, lm=(lambda x: (args[0].rsh(x) & 0xFFFFFFFF)))


class Data():

    def __init__(self, xpr=None, num=0):
        self.xpr = xpr
        self.num = num

    def getXpr(self):
        return self.xpr

    def getNum(self):
        return self.num

    def isXprType(self):
        return self.xpr is not None

    def isNumType(self):
        return self.xpr is None

    def getData(self, x):
        if self.isNumType():
            return self.num
        return self.xpr(x) + self.num

    def setDefiner(self, definer):
        self.definer = definer

    def getDefiner(self):
        return self.definer

    def __add__(self, value):
        if type(value) == int:
            if self.isNumType():
                return Data(num=((self.num + value) & 0xFFFFFFFF))
            else:
                return Data(xpr=self.xpr, num=((self.num + value) & 0xFFFFFFFF))
        else:
            if self.isNumType() and value.isNumType():
                return Data(num=((self.num + value.num) & 0xFFFFFFFF))
            else:
                num = self.num + value.num
                if self.isNumType():
                    return Data(xpr=lambda x: value.xpr(x), num=num)
                elif value.isNumType():
                    return Data(xpr=lambda x: self.xpr(x), num=num)
                else:
                    return Data(xpr=lambda x: self.xpr(x) + value.xpr(x), num=num)

    def __radd__(self, lhs):
        return self.__add__(lhs)

    def __or__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                return Data(num=self.num | rhs)
            else:
                return Data(xpr=lambda x: (self.xpr(x) + self.num) | rhs)
        else:
            if self.isNumType() and rhs.isNumType():
                return Data(num=self.num | rhs.num)
            else:
                return Data(xpr=lambda x: self.getData(x) | rhs.getData(x))

    def __ror__(self, rhs):
        return self.__or__(rhs)

    def __xor__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                return Data(num=self.num ^ rhs)
            else:
                return Data(xpr=lambda x: self.getData(x) ^ rhs)
        else:
            if self.isNumType() and rhs.isNumType():
                return Data(xpr=lambda x: (self.num) ^ (rhs.num))
            else:
                return Data(xpr=lambda x: (rhs.getData(x)) ^ (rhs.getData(x)))

    def __rxor__(self, lhs):
        return self.__xor__(lhs)

    def __and__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                return Data(num=self.num & rhs)
            else:
                return Data(xpr=lambda x: (self.xpr(x) + self.num) & rhs)
        else:
            if self.isNumType() and rhs.isNumType():
                return Data(num=self.num & rhs.num)
            else:
                return Data(xpr=lambda x: self.getData(x) & rhs.getData(x))

    def __rand__(self, lhs):
        return self.__and__(lhs)

    def __lshift__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                r = (self.num << (rhs % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: ((self.getData(x) << (rhs % 32)) & 0xFFFFFFFF))
        else:
            if self.isNumType() and rhs.isNumType():
                r = (self.num << (rhs.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: (self.getData(x) << (rhs.getData(x) % 32) & 0xFFFFFFFF))

    def __rlshift__(self, lhs):
        if type(lhs) == int:
            if self.isNumType():
                r = (lhs << (self.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: ((lhs << (self.getData(x) % 32)) & 0xFFFFFFFF))
        else:
            if self.isNumType() and lhs.isNumType():
                r = (lhs.num << (self.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: (lhs.getData(x) << (self.getData(x) % 32) & 0xFFFFFFFF))

    def lsh(self, x):
        if self.isNumType():
            r = (self.num << (x % 32)) & 0xFFFFFFFF
            return Data(num=r)
        else:
            # return Data(xpr=lambda y: (((self.xpr(y) + self.num) << x) & 0xFFFFFFFF))
            return Data(xpr=createLm(4, self.xpr, self.num))

    def __rshift__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                r = (self.num >> (rhs % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: ((self.getData(x) >> (rhs % 32)) & 0xFFFFFFFF))
        else:
            if self.isNumType() and rhs.isNumType():
                r = (self.num >> (rhs.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: (self.getData(x) >> (rhs.getData(x) % 32) & 0xFFFFFFFF))

    def __rrshift__(self, lhs):
        if type(lhs) == int:
            if self.isNumType():
                r = (lhs >> (self.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: ((lhs >> (self.getData(x) % 32)) & 0xFFFFFFFF))
        else:
            if self.isNumType() and lhs.isNumType():
                r = (lhs.num >> (self.num % 32)) & 0xFFFFFFFF
                return Data(num=r)
            else:
                return Data(xpr=lambda x: (lhs.getData(x) >> (self.getData(x) % 32) & 0xFFFFFFFF))

    def __mod__(self, rhs):
        if type(rhs) == int:
            if self.isNumType():
                return Data(num=self.num % rhs)
            else:
                return Data(xpr=lambda x: self.getData(x) % rhs)
        else:
            if self.isNumType() and rhs.isNumType():
                return Data(num=self.num % rhs.num)
            else:
                return Data(xpr=lambda x: (rhs.getData(x) % (self.getData(x))))

    def __rmod__(self, lhs):
        if type(lhs) == int:
            if self.isNumType():
                return Data(num=lhs % self.num)
            else:
                return Data(xpr=lambda x: lhs % self.getData(x))
        else:
            if self.isNumType() and lhs.isNumType():
                return Data(num=lhs.num % self.num)
            else:
                return Data(xpr=lambda x:self.getData(x) % (lhs.getData(x)))

    def rsh(self, x):
        if self.isNumType():
            r = (self.num >> (x % 32)) & 0xFFFFFFFF
            return Data(num=r)
        else:
            # return Data(xpr=lambda y: (((self.xpr(y) + self.num) >> x) & 0xFFFFFFFF))
            return Data(xpr=createLm(5, self.xpr, self.num))

    def xor(self, k):
        if type(k) == int:
            if self.isNumType():
                return Data(num=self.num ^ k)
            else:
                # return Data(xpr=lambda x: (self.xpr(x) + self.num) ^ k)
                return Data(xpr=createLm(6, self.xpr, self.num, k))
        else:
            if self.isNumType():
                # return Data(xpr=lambda x: (k.xpr(x) + k.num) ^ self.num)
                return Data(xpr=createLm(6, k.xpr, k.num, self.num))
            else:
                # return Data(xpr=lambda x: (self.xpr(x) + self.num) ^ (k.xpr(x) + k.num))
                return Data(xpr=createLm(7, self.xpr, self.num, k.xpr, k.num))

    def xAnd(self, k):
        if type(k) == int:
            if self.isNumType():
                return Data(num=self.num & k)
            else:
                # return Data(xpr=lambda x: (self.xpr(x) + self.num) & k)
                return Data(xpr=createLm(8, self.xpr, self.num, k))
        else:
            if self.isNumType():
                # return Data(xpr=lambda x: (k.xpr(x) + k.num) & self.num)
                return Data(xpr=createLm(9, k.xpr, k.num, self.num))
            else:
                # return Data(xpr=lambda x: (self.xpr(x) + self.num) & (k.xpr(x) + k.num))
                return Data(xpr=createLm(10, self.xpr, self.num, k.xpr, k.num))

    def __invert__(self):  # ~x
        if self.isNumType():
            return Data(num=~self.num)
        else:
            return Data(xpr=createLm(11, self.xpr, self.num))

    def xNot(self):
        if self.isNumType():
            return Data(num=~self.num)
        else:
            # return Data(xpr=lambda x: ~(self.xpr(x) + self.num))
            return Data(xpr=createLm(11, self.xpr, self.num))

    def rotateRight(self, x):
        x = x % 32
        if self.isNumType():
            return Data(num=rotate_right(self.num, x))
        else:
            # return Data(xpr=lambda y: (((self.rsh(y) & 0xFFFFFFFF ) | (self.lsh(32-y) & 0xFFFFFFFF )) & 0xFFFFFFFF ))
            return Data(xpr=createLm(12, self))

    def rotateLeft(self, x):
        x = x % 32
        if self.isNumType():
            return Data(num=rotate_left(self.num, x))
        else:
            # return Data( xpr=lambda y: ((self.lsh(y) & 0xFFFFFFFF ) | (self.rsh(32-y) & 0xFFFFFFFF )) )
            return Data(xpr=createLm(13, self))

    def rotateShift(self, x):
        x = x % 32
        if self.isNumType():
            return Data(num=((self.num >> x) & 0xFFFFFFFF))
        else:
            # return Data(xpr=lambda y: (self.rsh(y) & 0xFFFFFFFF))
            return Data(xpr=createLm(14, self))


def funcCH(e, f, g):
    # (E & F) ^ ((~E) & G)
    if e.isNumType() and f.isNumType() and g.isNumType():
        r = (e.num & f.num) ^ ((~e.num) & g.num)
        return Data(num=r)
    else:
        de = Data(num=e) if type(e) == int else e
        df = Data(num=f) if type(f) == int else f
        dg = Data(num=g) if type(g) == int else g
        return de.xAnd(df).xor(de.xNot().xAnd(dg))


def calcTmp1(h, s1, ch, k, w):
    # (H + SS1 + ch + K[j] + W[j]) & 0xFFFFFFFF
    if h.isNumType() and s1.isNumType() and ch.isNumType() and w.isNumType():
        r = (h.num + s1.num + ch.num + k + w.num) & 0xFFFFFFFF
        return Data(num=r)
    else:
        dh = Data(num=h) if type(h) == int else h
        ds1 = Data(num=s1) if type(s1) == int else s1
        dch = Data(num=ch) if type(ch) == int else ch
        dw = Data(num=w) if type(w) == int else w
        dk = Data(num=k)
        return (dh + ds1 + dch + dk + dw).xAnd(0xFFFFFFFF)


def funcMaj(a, b, c):
    if a.isNumType() and b.isNumType() and c.isNumType():
        r = (a.num & b.num) ^ (a.num & c.num) ^ (b.num & c.num)
        return Data(num=r)
    else:
        da = Data(num=a) if type(a) == int else a
        db = Data(num=b) if type(b) == int else b
        dc = Data(num=c) if type(c) == int else c
        return (da.xAnd(db)).xor(da.xAnd(dc)).xor(db.xAnd(dc)).xAnd(0xFFFFFFFF)


def funcBSIG0(x):
    if x.isNumType():
        return Data(num=rotate_right(x, 2) ^ (rotate_right(x, 13)) ^ (rotate_right(x, 22)))
    else:
        return x.rotateRight(2).xor(x.rotateRight(13)).xor(x.rotateRight(22))


def funcBSIG1(x):
    if x.isNumType():
        return Data(num=rotate_right(x, 6) ^ (rotate_right(x, 11)) ^ (rotate_right(x, 25)))
    else:
        return x.rotateRight(6).xor(x.rotateRight(11)).xor(x.rotateRight(25))


def funcSSIG0(x):
    if x.isNumType():
        return Data(num=rotate_right(x, 7) ^ (rotate_right(x, 18)) ^ (rotate_shift(x, 3)))
    else:
        return x.rotateRight(7).xor(x.rotateRight(8)).xor(x.rotateShift(13))


def funcSSIG1(x):
    if x.isNumType():
        return Data(num=rotate_right(x, 17) ^ (rotate_right(x, 19)) ^ (rotate_shift(x, 10)))
    else:
        return x.rotateRight(17).xor(x.rotateRight(19)).xor(x.rotateShift(10))


def calcTmp2(ss0, maj):
    # (SS0 + maj) & 0xFFFFFFFF
    if ss0.isNumType() and maj.isNumType():
        r = (ss0.num + maj.num) & 0xFFFFFFFF
        return Data(num=r)
    else:
        dss0 = Data(num=ss0) if type(ss0) == int else ss0
        dmaj = Data(num=maj) if type(maj) == int else maj
        return (dss0 + dmaj).xAnd(0xFFFFFFFF)


def rotate_left(a, k):
    k = k % 32
    return ((a << k) & 0xFFFFFFFF) | ((a & 0xFFFFFFFF) >> (32 - k))


def rotate_right(a, k):
    k = k % 32
    return (((a >> k) & 0xFFFFFFFF) | ((a & 0xFFFFFFFF) << (32 - k))) & 0xFFFFFFFF


def rotate_shift(a, k):
    k = k % 32
    return ((a >> k) & 0xFFFFFFFF)


def P_0(X):
    return (rotate_right(X, 7)) ^ (rotate_right(X, 18)) ^ (rotate_shift(X, 3))


def P_1(X):
    return (rotate_right(X, 17)) ^ (rotate_right(X, 19)) ^ (rotate_shift(X, 10))
