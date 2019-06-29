# coding=utf-8

import base64
import sys
from Crypto.PublicKey import RSA

sys.setrecursionlimit(10000000)


def readRsaKey(key):
    pem = open(key).read()
    pubKey = RSA.importKey(pem)
    n = pubKey.key.n
    print(len(str(n)))
    print(n)


def hextonumber(x):
    if x >= '0' and x <= '9':
        return int(x)
    elif x >= 'A' and x <= 'F':
        return ord(x) - 55
    else:
        return ord(x) - 87


def hextoflag(s):
    flag = ''
    i = 0
    while (i < len(s)):
        flag += chr(hextonumber(s[i]) * 16 + hextonumber(s[i + 1]))
        i += 2
    return flag


# base64解密
def b64(s):
    return base64.b64decode(s)


# base32解密
def b32(s):
    return base64.b32decode(s)


# 求两个数的最大公约数
def gcd(a, b):
    if a < b:
        a, b = b, a

    while b != 0:
        temp = a % b
        a = b
        b = temp

    return a


# 求满足ax+by=1，当gcd（a，b）=1时，满足式子的x和y
def egcd(a, b):
    if b == 0:
        return a, 1, 0
    else:
        g, x, y = egcd(b, a % b)
        return g, y, x - a / b * y


# quickpow，快速幂运算
def qp(n, m, p):
    ans = 1
    while (m):
        if (m % 2 == 1):
            ans = (ans * n) % p
        n = (n * n) % p
        m = m / 2
    return ans


# def egcd(a, b):
#     if a == 0:
#         return (b, 0, 1)
#     else:
#         g, y, x = egcd(b % a, a)
#         return (g, x - (b // a) * y, y)


# 求cd=1（mod m），在已知c，m，且gcd（c，m）=1的时候，求得c的逆元d
def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return (x + m) % m


# 求n的欧拉函数（这个是做RSA题专用的分解n，因为n是两个大素数相乘）
def get_phi_n(p, q):
    return (p - 1) * (q - 1)


# RSA公模攻击
def attacksamen(n, e1, e2, c1, c2):
    s = egcd(e1, e2)
    s1 = s[1]
    s2 = s[2]
    if s1 < 0:
        s1 = -s1
        c1 = modinv(c1, n)
    elif s2 < 0:
        s2 = -s2
        c2 = modinv(c2, n)
    m = (qp(c1, s1, n) * qp(c2, s2, n)) % n
    return hextoflag(str(hex(m))[2:-1])


def modequation(a, b, c):
    Gcd = gcd(a, c)
    if (b % Gcd != 0):
        return 'No Solution'
    a /= Gcd
    c /= Gcd
    b /= Gcd
    return b * modinv(a, c) % c


if __name__ == "__main__":
    readRsaKey('E:\\key\\rsa_public_key.pem')
