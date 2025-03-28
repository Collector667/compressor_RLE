
import numpy
import queue
import hashlib
import time
from bitArray import BitArray
import math








# LZ77
def LZ77_bit(S, buffer_size = 12):
    compressed = BitArray()
    buffer = bytearray()
    N = len(S)
    i = 0
    dyn_s = bytearray()
    while i < N:

        dyn_s.append(S[i])
        i += 1
        while buffer.__contains__(dyn_s) and i < N and len(dyn_s) < 255:
            dyn_s.append(S[i])
            i += 1
        dyn_s.pop(-1)
        i -= 1
        if len(dyn_s) == 0:
            x = BitArray()
            x.int_to_bitArray(0, buffer_size)
            compressed.append(x)
            x = BitArray()
            x.int_to_bitArray(0, 8)
            compressed.append(x)
            x = BitArray()
            x.int_to_bitArray(S[i], 8)
            compressed.append(x)
        else:
            index = buffer.index(dyn_s)
            x = BitArray()
            x.int_to_bitArray(index, buffer_size)
            compressed.append(x)
            x = BitArray()
            x.int_to_bitArray(len(dyn_s), 8)
            compressed.append(x)
            x = BitArray()
            x.int_to_bitArray(S[i], 8)
            compressed.append(x)
        i += 1
        if i > N:
            break
        for _ in range(len(dyn_s) + 1):
            buffer.append(S[i - len(dyn_s) - 1 + _])
        dyn_s = bytearray()
        while len(buffer) > 2**buffer_size:
            buffer.pop(0)
    compressed_S = compressed.bitArray_to_byteArray()
    compressed_S.insert(0, buffer_size)
    compressed_S.insert(0, len(compressed_S)*8 - (compressed.len()+8))
    return compressed_S

def LZ77(S, buffer_bits = 8):
    buffer_size = 2**buffer_bits
    compressed_S = bytearray()
    buffer = bytearray()
    N = len(S)
    i = 0
    dyn_s = bytearray()
    while i < N:
        dyn_s.append(S[i])
        i+=1
        while buffer.__contains__(dyn_s) and i < N:
            dyn_s.append(S[i])
            i+=1
        dyn_s.pop(-1)
        i-=1
        if len(dyn_s) == 0:
            compressed_S.append(0)
            compressed_S.append(0)
            if i >= N:
                compressed_S.append(255)
            else:
                compressed_S.append(S[i])
        else:
            index = buffer.index(dyn_s)
            compressed_S.append(index)
            compressed_S.append(len(dyn_s))
            compressed_S.append(S[i])
        i+=1
        if i > N:
            break
        for _ in range(len(dyn_s) + 1):
            buffer.append(S[i-len(dyn_s) - 1  + _])
        dyn_s = bytearray()
        while len(buffer)>buffer_size:
            buffer.pop(0)
    return compressed_S


# декодирование LZ77
def iLZ77_bit(compressed):
    compressed_bit = BitArray()
    compressed_bit.byteArray_to_bitArray(compressed)
    N = compressed_bit.len() - compressed[0]
    buffer_size = compressed[1]
    i = 16
    S = bytearray()
    buffer = bytearray()
    while i < N:
        index = BitArray()
        for _ in range(buffer_size):
            index.append_bit(compressed_bit.bitArray[i])
            i+=1
        l = BitArray()
        for _ in range(8):
            l.append_bit(compressed_bit.bitArray[i])
            i+=1
        symb = BitArray()
        for _ in range(8):
            symb.append_bit(compressed_bit.bitArray[i])
            i+=1
        for _ in range(l.bitArray_to_int()):
            S.append(buffer[index.bitArray_to_int()+_])
            buffer.append(buffer[index.bitArray_to_int()+_])
        S.append(symb.bitArray_to_int())
        buffer.append(symb.bitArray_to_int())
        while len(buffer) > 2**buffer_size:
            buffer.pop(0)
    return S
def iLZ77(compressed_message):
    S = bytearray()
    buffer = bytearray()
    buffer_len = 256
    N = len(compressed_message)
    i = 0
    while i < N:
        index = compressed_message[i]
        l = compressed_message[i+1]
        symb = compressed_message[i+2]
        i+=3
        for _ in range(l):
            S.append(buffer[index+_])
            buffer.append(buffer[index+_])
        S.append(symb)
        buffer.append(symb)
        while len(buffer) > buffer_len:
            buffer.pop(0)
    return S

class Dict_lz():
    def __init__(self, size= 256):
        self.dict = {}
        self.items = []
        self.idict = {}
        self.size = size
        self.flag = 1
        self.len = 0
    def __len__(self):
        return self.len
    def __add__(self, other):
        if self.len < self.size:
            self.dict[self.len] = other.copy()
            self.items.append(other.copy())

            self.idict[hashlib.sha256(other.copy()).hexdigest()] = self.len
            self.len +=1
        else:
            self.flag = 0
        return self

    def __contains__(self, i):
        return self.idict.__contains__(hashlib.sha256(i.copy()).hexdigest())
    def get_index(self, item):
        return self.idict[hashlib.sha256(item.copy()).hexdigest()]
    def get_item(self, k):
        return self.dict[k]
def LZ78(S):
    dict = Dict_lz()
    dict.__add__(bytearray())
    N = len(S)
    i = 0
    compressed = bytearray()
    symb = bytearray()
    while i < N:
        while dict.__contains__(symb) and i < N:
            symb.append(S[i])
            i+=1
        if dict.flag == 1:
            dict.__add__(symb)
        symb.pop(-1)
        compressed.append(dict.get_index(symb))
        compressed.append(S[i-1])
        symb = bytearray()
    return compressed

def LZ78_bit(S, size):
    dict_lz = Dict_lz(2**size)
    dict_lz += bytearray()

    N = len(S)
    i = 0
    compressed_bit = BitArray()
    symb = bytearray()
    t1 = time.time()
    while i < N:
        while dict_lz.__contains__(symb) and i<N:
            symb.append(S[i])
            i+=1
        if dict_lz.flag:
            dict_lz+=symb
        symb.pop(-1)
        x = BitArray()
        x.int_to_bitArray(dict_lz.get_index(symb), size)
        compressed_bit.append(x)
        x = BitArray()
        x.int_to_bitArray(S[i-1], 8)
        compressed_bit.append(x)
        symb = bytearray()
    t2 = time.time()
    print(t2-t1)
    compressed_S = compressed_bit.bitArray_to_byteArray()
    compressed_S.insert(0, size)
    compressed_S.insert(0, len(compressed_S)*8 - 8 - compressed_bit.len())
    return compressed_S

def iLZ78(S):
    dict_LZ = Dict_lz()
    dict_LZ.__add__(bytearray())
    decompress_S = bytearray()
    N = len(S)
    i = 0
    while i < N:
        temp = bytearray()
        for _ in dict_LZ.get_item(S[i]):
            temp.append(_)
            decompress_S.append(_)
        temp.append(S[i+1])
        decompress_S.append(S[i+1])
        i+=2
        if dict_LZ.flag == 1:
            dict_LZ.__add__(temp)
    return decompress_S
def iLZ78_bit(S):
    compressed_bit = BitArray()
    compressed_bit.byteArray_to_bitArray(S)
    N = compressed_bit.len()  - S[0]
    size= S[1]
    i = 16
    x1 = 0
    d = {0: bytearray()}
    x1+=1
    decompress_S = bytearray()
    while i < N:
        x = BitArray()
        for _ in range(size):
            x.append_bit(compressed_bit[i])
            i+=1
        temp = bytearray()
        for _ in d[x.bitArray_to_int()]:
            decompress_S.append(_)
            temp.append(_)
        x = BitArray()
        for _ in range(8):
            x.append_bit(compressed_bit[i])
            i+=1
        decompress_S.append(x.bitArray_to_int())
        temp.append(x.bitArray_to_int())
        if x1 < 2**size:
            d[x1] = temp
            x1+=1
    return decompress_S

def LZ78_bit_dyn(S, size = 20):
    dict_lz = Dict_lz(2**size)
    dict_lz += bytearray()
    N = len(S)
    i = 0
    compressed_bit = BitArray()
    symb = bytearray()
    while i < N:
        while dict_lz.__contains__(symb) and i<N:
            symb.append(S[i])
            i+=1
        if dict_lz.flag:
            dict_lz+=symb
        symb.pop(-1)
        x = BitArray()
        x.int_to_bitArray(dict_lz.get_index(symb), math.ceil(math.log2(dict_lz.len-1)))
        if math.ceil(math.log2(dict_lz.len -1)) == 0:
            x.int_to_bitArray(dict_lz.get_index(symb), 1)
        compressed_bit.append(x)
        x = BitArray()
        x.int_to_bitArray(S[i-1], 8)
        compressed_bit.append(x)
        symb = bytearray()
    compressed_S = compressed_bit.bitArray_to_byteArray()
    compressed_S.insert(0, size)
    compressed_S.insert(0, len(compressed_S)*8 - 8 - compressed_bit.len())
    return compressed_S

def iLZ78_bit_dyn(S):
    compressed_bit = BitArray()
    compressed_bit.byteArray_to_bitArray(S)
    N = compressed_bit.len()  - S[0]
    size= S[1]
    i = 16
    x1 = 0
    d = {0: bytearray()}
    dict_LZ = Dict_lz(2**size)
    dict_LZ.__add__(bytearray())
    x1+=1
    decompress_S = bytearray()
    while i < N:
        x = BitArray()
        if math.log2(dict_LZ.len) == 0:
            x.append_bit(compressed_bit[i])
            i += 1
        for _ in range(math.ceil(math.log2(dict_LZ.len))):
            x.append_bit(compressed_bit[i])
            i+=1
        temp = bytearray()
        for _ in dict_LZ.get_item(x.bitArray_to_int()):
            decompress_S.append(_)
            temp.append(_)
        x = BitArray()
        for _ in range(8):
            x.append_bit(compressed_bit[i])
            i+=1
        decompress_S.append(x.bitArray_to_int())
        temp.append(x.bitArray_to_int())
        if dict_LZ.flag:
            dict_LZ.__add__(temp)

    return decompress_S

def LZW(S, size = 14):
    dict_lz = Dict_lz(2 ** size)
    for _ in range(256):
        x = bytearray()
        x.append(_)
        dict_lz+=x
    print(dict_lz.dict)
    N = len(S)
    i = 0
    compressed_bit = BitArray()
    symb = bytearray()
    while i < N:
        while dict_lz.__contains__(symb) and i < N:
            symb.append(S[i])
            i += 1
        if dict_lz.flag:
            dict_lz += symb
        symb.pop(-1)
        i-=1
        x = BitArray()
        x.int_to_bitArray(dict_lz.get_index(symb), size)
        compressed_bit.append(x)
        symb = bytearray()
    compressed_S = compressed_bit.bitArray_to_byteArray()
    compressed_S.insert(0, size)
    compressed_S.insert(0, len(compressed_S) * 8 - 8 - compressed_bit.len())
    return compressed_S

def iLZW(S):
    compressed_bit = BitArray()
    compressed_bit.byteArray_to_bitArray(S)
    N = compressed_bit.len() - S[0]
    size = S[1]
    i = 16
    x1 = 0
    dict_LZ = Dict_lz(2 ** size)
    dict_LZ.__add__(bytearray())
    for _ in range(26):
        x = bytearray()
        x.append(97+_)
        dict_LZ+=x
    x1 += 1
    decompress_S = bytearray()

    while i < N:
        x = BitArray()
        if math.log2(dict_LZ.len) == 0:
            x.append_bit(compressed_bit[i])
            i += 1
        for _ in range(math.ceil(math.log2(dict_LZ.len))):
            x.append_bit(compressed_bit[i])
            i += 1
        temp = bytearray()
        for _ in dict_LZ.get_item(x.bitArray_to_int()):
            decompress_S.append(_)
            temp.append(_)
        x = BitArray()
        for _ in range(8):
            x.append_bit(compressed_bit[i])
            i += 1
        decompress_S.append(x.bitArray_to_int())
        temp.append(x.bitArray_to_int())
        if dict_LZ.flag:
            dict_LZ.__add__(temp)
    return decompress_S

def LZSS(S, buffer_size = 12):
    compressed = BitArray()
    buffer = bytearray()
    N = len(s)
    i = 0
    dyn_s = bytearray()
    while i < N:
        while buffer.__contains__(dyn_s) and i < N and len(dyn_s) < 255:
            dyn_s.append(S[i])
            i += 1
        if not buffer.__contains__(dyn_s):
            dyn_s.pop(-1)
            i -= 1
        if dyn_s.__len__() * 8 - (buffer_size + 8) > 0:
            compressed.append_bit(1)
            x = BitArray()
            index = buffer.index(dyn_s)
            x.int_to_bitArray(index, buffer_size)
            compressed.append(x)
            x = BitArray()
            x.int_to_bitArray(dyn_s.__len__(), 8)
            compressed.append(x)
            for _ in range(len(dyn_s)):
                buffer.append(S[i - len(dyn_s) + _])
        else:
            i-=dyn_s.__len__()
            x = BitArray()
            x.int_to_bitArray(S[i], 8)
            compressed.append_bit(0)
            compressed.append(x)
            buffer.append(S[i])
            i += 1
        if i > N:
            break
        dyn_s = bytearray()
        while len(buffer) > 2 ** buffer_size:
            buffer.pop(0)
    compressed_S = compressed.bitArray_to_byteArray()
    compressed_S.insert(0, buffer_size)
    compressed_S.insert(0, len(compressed_S) * 8 - (compressed.len() + 8))
    return compressed_S

def iLZSS(compressed):
    compressed_bit = BitArray()
    compressed_bit.byteArray_to_bitArray(compressed)
    N = compressed_bit.len() - compressed[0]
    buffer_size = compressed[1]
    i = 16
    S = bytearray()
    buffer = bytearray()
    while i < N:
        flag = compressed_bit[i]
        i+=1
        if flag:
            index = BitArray()
            for _ in range(buffer_size):
                index.append_bit(compressed_bit.bitArray[i])
                i+=1
            l = BitArray()
            for _ in range(8):
                l.append_bit(compressed_bit.bitArray[i])
                i+=1
            for _ in range(l.bitArray_to_int()):

                S.append(buffer[index.bitArray_to_int() + _])
                buffer.append(buffer[index.bitArray_to_int() + _])
        else:
            symb = BitArray()
            for _ in range(8):
                symb.append_bit(compressed_bit.bitArray[i])
                i+=1
            S.append(symb.bitArray_to_int())
            buffer.append(symb.bitArray_to_int())
        while len(buffer) > 2**buffer_size:
            buffer.pop(0)
    return S


file = open('enwik7.txt', 'rb')
s = file.read()
print(LZ77_bit(s, 12).__len__())
print(LZ77_bit(s, 14).__len__())
print(LZ77_bit(s, 16).__len__())