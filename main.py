# добавления повторный символов

from bitArray import BitArray


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


class Compressor_by_mahmudovm:
    def __init__(self, pathOrig , pathCompress = 'compressed'):
        self.path_compress = pathCompress
        self.path_orig = pathOrig
        self.path_decompress = "decompressed_" + pathOrig
    def RLE_decode(self):
        file = open(self.path_compress, "rb")
        compressed_S = file.read()
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
        file.close()
        file = open(self.path_decompress, 'wb')
        file.write(decompressed_S)
        file.close()
        return decompressed_S
    def RLE_bit(self, len_symbol = 8):
        if len_symbol < 1:
            len_symbol = 1
        file_input = open(self.path_orig, "rb")
        file_output = open(self.path_compress, "wb")
        S = bytearray(file_input.read())
        print(S)
        compressed_S_bits = BitArray()
        prev_bits = BitArray()
        S_bits = BitArray()
        S_bits.byteArray_to_bitArray(byteArray=S)
        print(S_bits.bitArray_to_byteArray())
        for _ in S_bits.bitArray[:len_symbol]:
            prev_bits.append_bit(_)
        counter = 1
        flag = False
        buffer_len = 127
        buffer = BitArray()
        symbol = BitArray()

        for bit in S_bits.bitArray[len_symbol:]:
            symbol.append_bit(bit)
            if symbol.len() == len_symbol:
                if symbol.equal(prev_bits):
                    if flag:
                        x = 0
                        if buffer_len > 255:
                            while buffer_len > 255:
                                buffer_len -= 127
                                z = bytearray()
                                z.append(255)
                                bits_255 = BitArray()
                                bits_255.append(bits_255)
                                compressed_S_bits.append(bits_255)
                                for _ in range(127 * len_symbol):
                                    compressed_S_bits.append_bit(buffer.bitArray[x + _])
                                x += 127 * len_symbol
                        if buffer_len > 128:
                            z = bytearray()
                            z.append(buffer_len)
                            bits_len = BitArray()
                            bits_len.byteArray_to_bitArray(z)
                            compressed_S_bits.append(bits_len)
                            for _ in range((buffer_len - 128) * len_symbol):
                                compressed_S_bits.append_bit(buffer.bitArray[x + _])
                        counter = 1
                else:
                    if counter == 1:
                        if not flag:
                            flag = True
                            buffer_len+=1
                        buffer.append(prev_bits)
                        buffer_len+=1
                    else:
                        if counter > 128:
                            while counter > 128:
                                counter -= 127
                                z = bytearray()
                                z.append(127)
                                bits_127 = BitArray()
                                bits_127.byteArray_to_bitArray(z)
                                compressed_S_bits.append(bits_127)
                                compressed_S_bits.append(prev_bits)
                        if counter > 0:
                            z = bytearray()
                            z.append(counter)
                            bits_counter = BitArray().byteArray_to_bitArray(z)
                            compressed_S_bits.append(bits_counter)
                            compressed_S_bits.append(prev_bits)
                prev_bits = symbol
                symbol = BitArray()
        if flag:
            buffer.append(prev_bits)
            buffer_len+=1
            x = 0
            if buffer_len > 255:
                while buffer_len > 255:
                    buffer_len -= 127
                    z = bytearray()
                    z.append(255)
                    bits_255 = BitArray()
                    bits_255.append(bits_255)
                    compressed_S_bits.append(bits_255)
                    for _ in range(127 * len_symbol):
                        compressed_S_bits.append(buffer.bitArray[x + _])
                    x += 127 * len_symbol
            if buffer_len > 128:

                z = bytearray()
                z.append(buffer_len)
                bits_len = BitArray()
                bits_len.byteArray_to_bitArray(z)
                compressed_S_bits.append(bits_len)
                for _ in range((buffer_len - 128) * len_symbol):
                    compressed_S_bits.append_bit(buffer.bitArray[x + _])
        else:
            if counter > 128:
                while counter > 128:
                    counter -= 127
                    z = bytearray()
                    z.append(127)
                    bits_127 = BitArray()
                    bits_127.byteArray_to_bitArray(z)
                    compressed_S_bits.append(bits_127)
                    compressed_S_bits.append(prev_bits)
            if counter > 0:
                z = bytearray()
                z.append(counter)
                bits_counter = BitArray()
                bits_counter.byteArray_to_bitArray(z)
                compressed_S_bits.append(bits_counter)
                compressed_S_bits.append(prev_bits)

        compressed_S = compressed_S_bits.bitArray_to_byteArray()
        file_output.write(compressed_S)
        file_input.close()
        file_output.close()
        return compressed_S
    def RLE(self, M = 8):
        len_symbol = M//8
        if len_symbol < 1:
            len_symbol = 1
        file_input = open(self.path_orig, "rb")
        file_output = open(self.path_compress, "wb")
        S = bytearray(file_input.read())
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
        file_output.write(compressed_S)
        file_input.close()
        file_output.close()
        return compressed_S
import bitArray
if __name__ == '__main__':
    # compress = Compressor_by_mahmudovm('rar')
    # x1 = compress.RLE()
    # x2 = compress.RLE_decode()
    # print(x1 == x2)
    # array = []
    # x = True
    # b = False
    # array.append(x)
    # print(array)
    # print(type(array[0]))
    T = Compressor_by_mahmudovm('some.txt')
    t1 = T.RLE_bit(8)
    t2 = T.RLE(8)
    print(t1 == t2)
    print(t1)
    print(t2)
