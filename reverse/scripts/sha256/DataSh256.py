# -- coding: utf-8 --
import hashlib
import struct
from XData import Data, DataXpr, funcSSIG0, funcSSIG1, funcBSIG0, funcBSIG1, funcCH, funcMaj, calcTmp1, calcTmp2  # , calcCH, calcTmp1, calcMaj, calcTmp2, createLm, DataXpr


def out_hex(data):
    for i in data:
        print("%08x" % i)

    print("\n")


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


IV = "0x6A09E667 0xBB67AE85 0x3C6EF372 0xA54FF53A 0x510E527F 0x9B05688C 0x1F83D9AB 0x5BE0CD19"

IV = IV.replace("0x", "")

IV = int(IV.replace(" ", ""), 16)

K = """0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2 """

K = K.replace("\n", "")
K = K.replace(", ", "")
K = K.replace(" ", "")
K = K.replace("0x", "")
K = int(K, 16)

a = []
for i in range(0, 8):
    a.append(0)
    a[i] = (IV >> ((7 - i) * 32)) & 0xFFFFFFFF

IV = a

k = []

for i in range(0, 64):
    k.append(0)
    k[i] = (K >> ((63 - i) * 32)) & 0xFFFFFFFF

K = k

indexValue = {}


def CF(V_i, B_i):
    W = []
    # 构造64个字
    # 其中前16个字直接由消息的第i个块分解得到

    for j in range(0, 16):
        W.append(0)
        unpack_list = struct.unpack(">I", B_i[j * 4:(j + 1) * 4])
        W[j] = unpack_list[0]
        if j == 0:
            indexValue['0'] = Data(xpr=DataXpr(ltype=0, lm=(lambda x: x)))
        else:
            indexValue[str(j)] = Data(num=W[j])

    for j in range(16, 64):
        W.append(0)
        s0 = P_0(W[j - 15])
        s1 = P_1(W[j - 2])
        W[j] = (W[j - 16] + s0 + W[j - 7] + s1) & 0xFFFFFFFF

        xdata = indexValue[str(j - 16)] + funcSSIG0(indexValue[str(j - 15)]) + indexValue[str(j - 7)] + funcSSIG1(indexValue[str(j - 2)])
        indexValue[str(j)] = xdata & (0xFFFFFFFF)

    A, B, C, D, E, F, G, H = V_i

    """
    S1 := (e rightrotate 6) xor (e rightrotate 11) xor (e rightrotate 25)
    ch := (e and f) xor ((not e) and g)
    temp1 := h + S1 + ch + k[i] + w[i]
    S0 := (a rightrotate 2) xor (a rightrotate 13) xor (a rightrotate 22)
    maj := (a and b) xor (a and c) xor (b and c)
    temp2 := S0 + maj

    h := g
    g := f
    f := e
    e := d + temp1
    d := c
    c := b
    b := a
    a := temp1 + temp2
    T1 = H + LSigma_1(E) + Conditional(E, F, G) + K[i] + W[i];
    T2 = LSigma_0(A) + Majority(A, B, C);
    """

    encA = Data(num=A)
    encB = Data(num=B)
    encC = Data(num=C)
    encD = Data(num=D)
    encE = Data(num=E)
    encF = Data(num=F)
    encG = Data(num=G)
    encH = Data(num=H)

    # 进行64次循环加密
    for j in range(0, 64):
        SS1 = rotate_right(E, 6) ^ rotate_right(E, 11) ^ rotate_right(E, 25)
        SS0 = rotate_right(A, 2) ^ rotate_right(A, 13) ^ rotate_right(A, 22)
        ch = (E & F) ^ ((~E) & G)
        temp1 = (H + SS1 + ch + K[j] + W[j]) & 0xFFFFFFFF
        maj = (A & B) ^ (A & C) ^ (B & C)
        temp2 = (SS0 + maj) & 0xFFFFFFFF

        H = G
        G = F
        F = E
        E = (D + temp1)
        D = C
        C = B
        B = A
        A = (temp1 + temp2)

        A = A & 0xFFFFFFFF
        B = B & 0xFFFFFFFF
        C = C & 0xFFFFFFFF
        D = D & 0xFFFFFFFF
        E = E & 0xFFFFFFFF
        F = F & 0xFFFFFFFF
        G = G & 0xFFFFFFFF
        H = H & 0xFFFFFFFF

        xss1 = funcBSIG1(encE)  # .getSS1()
        xss0 = funcBSIG0(encA)  # .getSS0()
        xch = funcCH(encE, encF, encG)
        xtmp1 = calcTmp1(encH, xss1, xch, K[j], indexValue[str(j)])
        xmaj = funcMaj(encA, encB, encC)
        xtmp2 = calcTmp2(xss0, xmaj)

        encH = encG
        encG = encF
        encF = encE
        encE = (encD + xtmp1)
        encD = encC
        encC = encB
        encB = encA
        encA = (xtmp1 + xtmp2)

        encA = encA & (0xFFFFFFFF)
        encB = encB & (0xFFFFFFFF)
        encC = encC & (0xFFFFFFFF)
        encD = encD & (0xFFFFFFFF)
        encE = encE & (0xFFFFFFFF)
        encF = encF & (0xFFFFFFFF)
        encG = encG & (0xFFFFFFFF)
        encH = encH & (0xFFFFFFFF)

    print("After Encode: ")
    print(A, B, C, D, E, F, G, H)

    V_i_1 = []
    V_i_1.append((A + V_i[0]) & 0xFFFFFFFF)
    V_i_1.append((B + V_i[1]) & 0xFFFFFFFF)
    V_i_1.append((C + V_i[2]) & 0xFFFFFFFF)
    V_i_1.append((D + V_i[3]) & 0xFFFFFFFF)
    V_i_1.append((E + V_i[4]) & 0xFFFFFFFF)
    V_i_1.append((F + V_i[5]) & 0xFFFFFFFF)
    V_i_1.append((G + V_i[6]) & 0xFFFFFFFF)
    V_i_1.append((H + V_i[7]) & 0xFFFFFFFF)

    XV_i_1 = []
    XV_i_1.append((encA + V_i[0]) & (0xFFFFFFFF))
    XV_i_1.append((encB + V_i[1]) & (0xFFFFFFFF))
    XV_i_1.append((encC + V_i[2]) & (0xFFFFFFFF))
    XV_i_1.append((encD + V_i[3]) & (0xFFFFFFFF))
    XV_i_1.append((encE + V_i[4]) & (0xFFFFFFFF))
    XV_i_1.append((encF + V_i[5]) & (0xFFFFFFFF))
    XV_i_1.append((encG + V_i[6]) & (0xFFFFFFFF))
    XV_i_1.append((encH + V_i[7]) & (0xFFFFFFFF))

    # print(encA)
    print(encA.xpr)
    print(encA.num)
    return V_i_1


def hash_msg(msg):
    # 信息预处理
    msgLen = len(msg)
    reserve1 = msgLen % 64
    # 附加填充比特 1 0 0 0  ....   488
    preProcessingMsg = msg.encode() + struct.pack("B", 128)  # unsignedchar 1000 0000
    reserve1 = reserve1 + 1
    for i in range(reserve1, 56):
        preProcessingMsg = preProcessingMsg + struct.pack("B", 0)

    bit_length = (msgLen) * 8
    bit_length_string = struct.pack(">Q", bit_length)  # big-endian unsignedlonglong
    # 附加长度值
    preProcessingMsg = preProcessingMsg + bit_length_string

    print(f'preProcessingMsg length: {len(preProcessingMsg)}')
    group_count = int(len(preProcessingMsg) / 64)
    print(f'group count: {group_count}')

    # break message into 512-bit chunks
    B = []
    for i in range(0, group_count):
        B.append(0)
        B[i] = preProcessingMsg[i * 64:(i + 1) * 64]

    print(f'chunks: {B}')

    V = []
    V.append(0)
    V[0] = IV
    # mapping
    for i in range(0, group_count):
        V.append(0)
        V[i + 1] = CF(V[i], B[i])

    # print(i)
    return V[group_count]


src = "yyyyWKPjdffgbP8nuTk0"
print(src)
y = hash_msg(src)
print("result: ")
print(y)
out_hex(y)

sh = hashlib.sha256()
print(hashlib.sha256(src.encode()).hexdigest())
