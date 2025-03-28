import numpy as np
from PIL import Image
from numpy.ma.core import compress

import haffman
import SA_IS
from LZ import LZ77_bit, LZ78_bit, LZ78_bit_dyn, iLZ77_bit, iLZ78_bit_dyn, iLZ78, iLZ78_bit
from SA_IS import S_index, better_iBWT
from haffman import entropy, count_symb


def encode_repeat_append(counter, compressed_S, prev_symbol, len_symbol):
    if counter > 128:
        while counter > 128:
            counter -= 127
            compressed_S.append(127)
            for _ in prev_symbol:
                compressed_S.append(_)
    if counter > 0:
        compressed_S.append(counter)
        for _ in range(len_symbol):
            compressed_S.append(prev_symbol[_])
#добавления неповтор символов
def encode_unrepeated_append(compressed_S, len_symbol, buffer, buffer_len):
    x = 0
    if buffer_len > 255:
        while buffer_len > 255:
            buffer_len -= 127
            compressed_S.append(255)
            for _ in range(127 * len_symbol):
                compressed_S.append(buffer[x + _])
            x += 127 * len_symbol
    if buffer_len > 128:
        compressed_S.append(buffer_len)
        for _ in range((buffer_len - 128) * len_symbol):
            compressed_S.append(buffer[x + _])

def RLE_decode(compressed_S):
    N = len(compressed_S)
    decompressed_S = bytearray()
    i = 1
    len_symbol = compressed_S[0]
    #кол-во байт с кодировкой
    N_encode = ((N-1)//len_symbol) * len_symbol
    while i < N_encode:
        if compressed_S[i] <= 128:
            for _ in range(compressed_S[i]):
                for q in range(len_symbol):
                    decompressed_S.append(compressed_S[i + q + 1])
            i += 1 + len_symbol
        else:
            l = compressed_S[i] - 128
            for _ in range(l*len_symbol):
                decompressed_S.append(compressed_S[i+1])
                i+=1
            i+=1
    #запись кода без кодировки
    while i < N:
        decompressed_S.append(compressed_S[i])
        i+=1
    return decompressed_S
def RLE(S, M = 8):
    len_symbol = M//8
    if len_symbol < 1:
        len_symbol = 1
    compressed_S = bytearray()
    compressed_S.append(len_symbol)
    prev_symbol = bytearray()
    for i in range(len_symbol):
        prev_symbol.append(S[i])
    counter = 1
    flag = False
    buffer_len = 127
    buffer = bytearray()
    symbol = bytearray()
    for byte_S in S[len_symbol:]:
        symbol.append(byte_S)
        if len(symbol) == len_symbol:
            if symbol == prev_symbol:
                if flag:
                    encode_unrepeated_append(compressed_S, len_symbol, buffer, buffer_len)
                    flag = False
                    buffer_len = 127
                    buffer = bytearray()
                counter+=1
            else:
                if counter == 1:
                    if not flag:
                        flag = True
                        buffer_len+=1
                    for _ in prev_symbol:
                        buffer.append(_)
                    buffer_len += 1
                else:
                    encode_repeat_append(counter, compressed_S, prev_symbol, len_symbol)
                    counter = 1
            prev_symbol = symbol
            symbol = bytearray()
    if flag:
        for _ in range(len_symbol):
            buffer.append(prev_symbol[_])
        buffer_len+=1
        encode_unrepeated_append(compressed_S, len_symbol, buffer, buffer_len)
    else:
        encode_repeat_append(counter, compressed_S, prev_symbol,len_symbol)
    if len(symbol) < len_symbol:
        for _ in symbol:
            compressed_S.append(_)
    return compressed_S


#parametr HA = 1, RLE = 2, BWT+RLE = 3,
# BWT+MTF+HA = 4, BWT+MTF+RLE+HA = 5,
# LZ77 = 6, LZ77+HA = 7, LZ78 = 8,
# LZ78+HA = 9, LZSS = 10, LZW = 11
def Compressor(S, parametr):
    if parametr == 1:
        dict_HA = haffman.huffman_algorithm(S)
        compressed_S = haffman.huffman_compress(S, dict_HA)
        compressed_S.insert(0, 1)
    elif parametr == 2:
        compressed_S = RLE(S)
        compressed_S.insert(0, 2)
    elif parametr == 3:
        S_BWT = SA_IS.BWT(S)
        compressed_S = RLE(S_BWT)
        compressed_S.insert(0, 3)
    elif parametr == 4:
        S_BWT = SA_IS.BWT(S)
        S_MTF = haffman.MTF(S_BWT)
        dict_HA = haffman.huffman_algorithm(S_MTF)
        compressed_S = haffman.huffman_compress(S_MTF, dict_HA)
        compressed_S.insert(0, 4)
    elif parametr == 5:
        S_BWT = SA_IS.BWT(S)
        S_MTF = haffman.MTF(S_BWT)
        S_RLE = RLE(S_MTF)
        dict_HA = haffman.huffman_algorithm(S_RLE)
        compressed_S = haffman.huffman_compress(S_RLE, dict_HA)
        compressed_S.insert(0, 5)
    elif parametr == 6:
        compressed_S = LZ77_bit(S, 12)
        compressed_S.insert(0, 6)
    elif parametr == 7:
        compressed_S = LZ77_bit(S, 16)
        dict_HA = haffman.huffman_algorithm(compressed_S)
        compressed_S = haffman.huffman_compress(compressed_S, dict_HA)
        compressed_S.insert(0, 7)
    elif parametr == 8:
        compressed_S = LZ78_bit_dyn(S, 30)
        compressed_S.insert(0, 8)
    elif parametr == 9:
        compressed_S = LZ78_bit(S, 16)
    else:
        compressed_S = S
    return compressed_S

def deCompressor(compressed_S):
    if compressed_S[0] == 1:
        compressed_S.pop(0)
        compressed_S = haffman.huffman_decompress(compressed_S)
    elif compressed_S[0] == 2:
        compressed_S.pop(0)
        compressed_S = RLE_decode(compressed_S)
    elif compressed_S[0] == 3:
        compressed_S.pop(0)
        compressed_S = RLE_decode(compressed_S)
        compressed_S = better_iBWT(compressed_S, S_index(compressed_S))
    elif compressed_S[0] == 4:
        compressed_S.pop(0)
        compressed_S = haffman.huffman_decompress(compressed_S)
        compressed_S = haffman.iMTF(compressed_S)
        compressed_S = better_iBWT(compressed_S, S_index(compressed_S))
    elif compressed_S[0] == 5:
        compressed_S.pop(0)
        compressed_S = haffman.huffman_decompress(compressed_S)
        compressed_S = RLE_decode(compressed_S)
        compressed_S = haffman.iMTF(compressed_S)
        compressed_S = better_iBWT(compressed_S, S_index(compressed_S))
    elif compressed_S[0] == 6:
        compressed_S.pop(0)
        compressed_S = iLZ77_bit(compressed_S)
    elif compressed_S[0] == 8:
        compressed_S.pop(0)
        compressed_S = iLZ78_bit_dyn(compressed_S)
    elif compressed_S[0] == 7:
        compressed_S.pop(0)
        compressed_S = haffman.huffman_decompress(compressed_S)
        compressed_S = iLZ77_bit(compressed_S)
    elif compressed_S[0] == 9:
        compressed_S.pop(0)
        compressed_S = haffman.huffman_decompress(compressed_S)
        compressed_S = iLZ78_bit(compressed_S)
    else:
        compressed_S = compressed_S
    return compressed_S

def png_to_raw(image_path, output_path):
    image = Image.open(image_path)
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        # Удаляем альфа-канал
        image = image.convert('RGB')

    raw_pixels = np.array(image)
    raw_data = raw_pixels.tobytes()

    with open(output_path, 'wb') as f:
        f.write(raw_data)
# if __name__ == '__main__':
#     file = open('enwik7.txt', 'rb')
#     s = file.read()
#     arr = []
#     x= bytearray()
#     s = bytearray(s)
#     for i in range(1000):
#         for _ in range(10**4):
#             x.append(s[i*10**4 + _])
#         arr.append(x)
#         x = bytearray()
#     z = bytearray()
#
#     for _ in arr:
#
#         t = SA_IS.BWT(_)
#         t2 = haffman.MTF(t)
#         for j in t2:
#             z.append(j)
#     print(haffman.en(z))
    #-491805.02175961365




