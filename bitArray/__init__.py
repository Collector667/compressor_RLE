

class BitArray:
    def __init__(self):
        self.bitArray = []
    def __getitem__(self, item):
        return self.bitArray[item]
    def equal(self, other):
        flag = False
        if self.len() == other.len():
            flag = True
            for _ in range(self.len()):
                if self.bitArray[_] != other.bitArray[_]:
                    flag = False
        return flag
    def plus_one(self):
        x = self.len() - 1
        flag = True
        while flag:
            if self.bitArray[x] == 0:
                self.bitArray[x] = 1
                flag = False
            else:
                self.bitArray[x] = 0
                x -= 1
                if x == -1:
                    flag = False
    def reverse_append_bit(self, bit):
        type_error = False
        bit_Array = BitArray()
        try:
            if bit == 1:
                bit_Array.bitArray.append(1)
                bit_Array.append(self)
                self.bitArray = bit_Array.bitArray
            elif bit == 0:
                bit_Array.bitArray.append(0)
                bit_Array.append(self)
                self.bitArray = bit_Array.bitArray
            else:
                type_error = True
        except type_error:
            print('Добавляемый бит не является булевым')
    def append_bit(self, bit):
        type_error = False
        try:
            if bit == 1:
                self.bitArray.append(1)
            elif bit == 0:
                self.bitArray.append(0)
            else:
                type_error = True
        except type_error:
            print('Добавляемый бит не является булевым')
    def append(self, newBitArray):
        type_error = False
        try:
            if type(self) != type(newBitArray):
                type_error = True
        except type_error:
            print('Добавляемый массив не является булевым')
        for _ in newBitArray.bitArray:
            self.append_bit(_)
    def len(self):
        count = 0
        for _ in self.bitArray:
            count+=1
        return count
    def array(self):
        arr = []
        for _ in self.bitArray:
            arr.append(_)
        return arr
    def int_to_bitArray(self, x, len):
        for _ in range(len, 0 , -1):
            if x - 2**(_-1) >= 0:
                self.bitArray.append(1)
                x-=2**(_-1)
            else:
                self.bitArray.append(0)
    def bitArray_to_byteArray(self):
        n = self.len()
        N = n//8
        array = bytearray()
        for _ in range(N):
            x = 0
            for i in range(8):
                j = self.bitArray[_*8+i]
                x+= j*(2**(8-i-1))
            array.append(x)
        #запись в байт неполный набор бит (аля 1101 в байт 11010000 так как записать можно только байты)
        x = 0
        for _ in range(n-N*8):
            j = self.bitArray[N * 8 + _]
            x += j * (2 ** (8 - _ - 1))
        if n-N*8 > 0:
            array.append(x)
        return array
    def byte(self):
        array = bytearray()
        x = 0
        for i in range(8):
            j = self.bitArray[i]
            x += j * (2 ** (8 - i - 1))
        array.append(x)
        return array
    # def bitArray_to_int(self):
    #     x = 0
    #     N = self.len()//8
    #     for _ in range(N):
    #         x = 0
    #         for i in range(8):
    #             j = self.bitArray[_*8+i]
    #             x+= j*(2**(8-i-1))
    #     return x
    def bitArray_to_int(self):
        x = 0
        N = self.len()
        for i in range(N, 0, -1):
            x+= self.bitArray[N-i] * 2**(i-1)
        return x
    def delete(self, index):
        if index < self.len() - 1:
            return self.bitArray[0:index].append(self.bitArray[index+1:])
        else:
            return self.bitArray[0:index]
    def byteArray_to_bitArray(self, byteArray, lastByte_bits = 0):
        type_error = False
        try:
            if type(byteArray) != type(bytearray()):
                type_error = True

        except type_error:
            print('Массив не является байтовым')
        base = 2
        for _ in byteArray:
            x = _
            buffer = []
            for i in range(8):
                buffer.append(x%base)
                x //= base
            for i in range(8):
                self.bitArray.append(buffer[7-i])
        for i in range(lastByte_bits):
            self.delete(self.len()-1)
    def hash(self):
        s = ''
        for _ in self.bitArray:
            s+=str(self)
        return s