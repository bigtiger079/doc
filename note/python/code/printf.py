from ctypes import *

# 调用系统C库
msvcrt = cdll.LoadLibrary('msvcrt.dll')
msvcrt.printf(b"Testing: %s\n", b'Hello ctypes!')

# string_buffer
p = create_string_buffer(5)
print(sizeof(p))
print(repr(p.raw))
p.raw = b'Hello'
print(repr(p.raw))
print(repr(p.value))


# C Struct
class beer_recipe(Structure):
    _fields_ = [
        ("amt_barley", c_int),
        ("amt_water", c_int)
    ]