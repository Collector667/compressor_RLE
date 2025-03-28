import math
import queue
from pickletools import pybytes_or_str
from queue import PriorityQueue
from sys import flags
from zlib import decompress

from numpy.ma.core import array, compress

from SA_IS import buildTypeMap
from bitArray import BitArray
import numpy
def prob_estimate(S):
    # P = [0 for i in range(128)]

    P  = numpy.array([0 for i in range(256)])
    N = len(P)
    for s in S:
        P[s]+=1
    P = P/N
    return P
def count_symb(S):
    # P = [0 for i in range(128)]

    counters = numpy.array([0 for i in range(256)])
    N = len(counters)
    for s in S:
        counters[s]+=1
    return counters
def entropy(S):
    P = prob_estimate(S)
    P = numpy.array(list(filter(lambda x: x>0, P)))
    H = -sum(numpy.log2(P) *P)
    return H

def counts (S):
    counters = [0 for _ in range(256)]
    for _ in S:
        counters[_] += 1
    return counters
def en(S):
    conters = counts(S)
    N = len(S)
    sum = 0
    for _ in conters:
        if _ != 0:
            sum = sum + (_/N) *math.log2(N/_)
    return sum
def MTF(S):
    table_MTF = [i for i in range(256)]
    L = []
    new_S = bytearray()
    for s in S:
        L.append(table_MTF.index(s))
        index = table_MTF.index(s)
        new_S.append(index)
        table_MTF = [table_MTF[index] ] + table_MTF[0: index] + table_MTF[index+1: ]
    return new_S
def iMTF(S):
    T = [i for i in range(256)]
    S_new = bytearray()
    for s in S:
        i = s
        S_new.append(T[i])
        T = [T[i]] + T[:i] + T[i+1:]
    return S_new
def huffman_algorithm(S):
    N = len(S)
    counters = count_symb(S)
    Q = queue.PriorityQueue()
    list_of_list = []
    for i in range(256):
        if counters[i] != 0:
            new_Node = Node(symbol= i, count= counters[i])
            Q.put(new_Node)
            list_of_list.append(new_Node)
    while Q.qsize() >= 2:
        node_L = Q.get()
        node_R = Q.get()
        parent_counter = node_L.count + node_R.count
        parent_symb = node_L.symbol + node_R.symbol
        parent_node = Node(symbol= parent_symb ,count=parent_counter,lc= node_L, rc =node_R)
        node_R.parent = parent_node
        node_L.parent = parent_node
        Q.put(parent_node)
    codes = []
    dict = {}
    for l in list_of_list:
        node = l
        symbol = node.symbol
        code = BitArray()
        while node.parent != None:
            if node.parent.lc == node:
                code.reverse_append_bit(0)
            else:
                code.reverse_append_bit(1)
            node = node.parent
        codes.append(code)
        dict[symbol] = code.len()
    temp_dict = (sorted(dict.items(), key=lambda item: item[1]))
    dict = {}
    code = BitArray()
    z = BitArray()
    for _ in range(temp_dict[0][1]):
        code.reverse_append_bit(0)
    z.bitArray = code.array()
    dict[temp_dict[0][0]] = z
    for item in temp_dict[1:]:
        if item[1] == code.len():
            new_code = BitArray()
            new_code.bitArray = code.array()
            new_code.plus_one()
        else:
            new_code = BitArray()
            new_code.bitArray = code.array()
            new_code.plus_one()
            for _ in range(item[1] - code.len()):
                new_code.append_bit(0)
        dict[item[0]] = new_code
        code.bitArray = new_code.array()
    return dict

def mean_code_length(codes, S):
    return

class Node:
    def __init__(self, symbol, count, lc = None, rc = None, parent = None):
        self.symbol = symbol
        self.count = count
        self.lc = lc
        self.rc = rc
        self.parent = parent
    def __lt__(self, other):
        return self.count < other.count

def codes_to_len(codes):
    symbol_len = {}
    for item in codes.items():
        sym = item[0]
        symbol_len[sym] = item.len()
    return symbol_len

def len_to_codes(symbol_len):
    symbol_len = dict(sorted(symbol_len.items(), key=lambda item: item[1]))
    codes = {}
    i = 0
    for item in symbol_len.items():
        symbol = item[0]
        L = item[1]
        if i == 0:
            code = 0
        else:
            code = (prev + 1) * 2**(L-prev_L)
        i+=1
        prev = code
        prev_L = L
    return codes

def bits_str(arr):
    s = ''
    for _ in arr:
        s+=str(_)
    return s
def huffman_compress(S, dict):
    max_len = 0
    for item in dict.items():
        if max_len < item[1].len():
            max_len = item[1].len()
    compressed_S = BitArray()

    for item in dict.items():
        z = bytearray()
        z.append(item[0])
        x = BitArray()
        x.byteArray_to_bitArray(z)
        compressed_S.append(x)
        x = BitArray()
        x.int_to_bitArray(item[1].len(), max_len)
        compressed_S.append(x)
    for i in range(8):
        compressed_S.bitArray.append(1)
    for i in S:
        compressed_S.append(dict[i])
    m = (8 - compressed_S.len()%8) %8
    Compressed_S_byte = compressed_S.bitArray_to_byteArray()
    Compressed_S_byte.insert(0, max_len)
    Compressed_S_byte.insert(0, m)
    return Compressed_S_byte

def huffman_decompress(S):
    max_len = S[1]
    symb = BitArray()
    i = 16
    S_bits = BitArray()
    S_bits.byteArray_to_bitArray(S)
    mas = []
    len_sym = BitArray()
    flag = True
    while flag:
        for _ in range(8):
            symb.append_bit(S_bits.bitArray[i])
            i+=1
        for _ in range(max_len):
            len_sym.append_bit(S_bits.bitArray[i])
            i+=1
        if symb.bitArray == [1, 1, 1, 1, 1, 1, 1, 1]:
            flag = False
        else:
            mas.append([len_sym.bitArray_to_int(), symb.bitArray_to_int()])
        symb = BitArray()
        len_sym = BitArray()
    dict = {}
    code = BitArray()
    z = BitArray()
    for _ in range(mas[0][0]):
        code.reverse_append_bit(0)
    z.bitArray = code.array()
    dict[bits_str(z.bitArray)] = mas[0][1]
    for item in mas[1:]:
        if item[0] == code.len():
            new_code = BitArray()
            new_code.bitArray = code.array()
            new_code.plus_one()
        else:
            new_code = BitArray()
            new_code.bitArray = code.array()
            new_code.plus_one()
            for _ in range(item[0] - code.len()):
                new_code.append_bit(0)
        dict[bits_str(new_code.bitArray)] = item[1]
        code.bitArray = new_code.array()
    i-=max_len

    decompressed = bytearray()
    D = BitArray()
    while i <= (len(S) * 8 - S[0]):
        # if symb.len() < min_len:
        #     for _ in range(min_len - symb.len()):
        #         symb.append_bit(S_bits.bitArray[i])
        #         i+=1
        if dict.__contains__(bits_str(symb.bitArray)):
            decompressed.append(dict[bits_str(symb.bitArray)])
            D.append(symb)
            symb = BitArray()
        else:
            symb.append_bit(S_bits.bitArray[i])
            i+=1
    return decompressed

def LZ77_byte(S):
    compressed = BitArray()
    buffer_size = 8
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
        while len(buffer) > 2 ** buffer_size:
            buffer.pop(0)
    compressed_S = compressed.bitArray_to_byteArray()
    compressed_S.insert(0, buffer_size)
    compressed_S.insert(0, len(compressed_S) * 8 - (compressed.len() + 8))
    return compressed_S




# file = open('enwik7.txt', 'rb')
# s = file.read()
#
# s= bytearray(s)
# t = MTF(s)
# print(iMTF(t) == s)
# print('----')
