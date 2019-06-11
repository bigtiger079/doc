
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


def x_right_shift(a, k):
    k = k % 32
    return limit(int(a / (1 << k)))


def x_left_shift(a, k):
    k = k % 32
    return limit(a * (1 << k))


def xor(A, B):
    return (A & ~B) | (B & ~A)


def limit(a):
    max_ = (1 << 32)
    over = int(a / max_)
    return a - int(over * max_)
