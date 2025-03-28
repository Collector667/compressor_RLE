import hashlib
import time

S_TYPE = ord("S")
L_TYPE = ord("L")

def naivelyMakeSuffixArray(source):
    suffixes = []
    for offset in range(len(source) + 1):
         suffixes.append(source[offset:])
    suffixes.sort()
    suffixArray = []
    for suffix in suffixes:
        offset = len(source) - len(suffix)
        suffixArray.append(offset)
    return suffixArray

def buildTypeMap(data):
    res = bytearray(len(data) + 1)
    res[-1] = S_TYPE
    if not len(data):
        return res
    res[-2] = L_TYPE
    for i in range(len(data)-2, -1, -1):
        if data[i] > data[i+1]:
            res[i] = L_TYPE
        elif data[i] == data[i+1] and res[i+1] == 1:
            res[i] = L_TYPE
        else:
            res[i] = S_TYPE

    return res

def findBucketSizes(string, alphabetSize=256):
    res = [0] * alphabetSize
    for char in string:
         res[char] += 1
    return res

def findBucketHeads(bucketSizes):
    offset = 1
    res = []
    for size in bucketSizes:
       res.append(offset)
       offset += size
    return res

def findBucketTails(bucketSizes):
    offset = 1
    res = []
    for size in bucketSizes:
        offset += size
        res.append(offset - 1)
    return res

def showSuffixArray(arr, pos=None):
    print(" ".join("%02d" % each for each in arr))
    if pos is not None:
        print(" ".join(
                "^^" if each == pos else "  "
               for each in range(len(arr))))

def guessLMSSort(string, bucketSizes, typemap):
    guessedSuffixArray = [-1] * (len(string) + 1)
    bucketTails = findBucketTails(bucketSizes)
    for i in range(len(string)):
        if not isLMSChar(i, typemap):
           continue
        bucketIndex = string[i]
        guessedSuffixArray[bucketTails[bucketIndex]] = i
        bucketTails[bucketIndex] -= 1
        #showSuffixArray(guessedSuffixArray)
    guessedSuffixArray[0] = len(string)

    #showSuffixArray(guessedSuffixArray)
    return guessedSuffixArray

def induceSortL(string, guessedSuffixArray, bucketSizes, typemap):
    bucketHeads = findBucketHeads(bucketSizes)
    for i in range(len(guessedSuffixArray)):
        if guessedSuffixArray[i] == -1:
            continue
        j = guessedSuffixArray[i] - 1
        if j < 0:
            continue
        if typemap[j] != L_TYPE:
            continue
        bucketIndex = string[j]
        guessedSuffixArray[bucketHeads[bucketIndex]] = j
        bucketHeads[bucketIndex] += 1
        #showSuffixArray(guessedSuffixArray, i)

def induceSortS(string, guessedSuffixArray, bucketSizes, typemap):
    bucketTails = findBucketTails(bucketSizes)

    for i in range(len(guessedSuffixArray)-1, -1, -1):
        j = guessedSuffixArray[i] - 1
        if j < 0:
            continue
        if typemap[j] != S_TYPE:
            continue
        bucketIndex = string[j]
        guessedSuffixArray[bucketTails[bucketIndex]] = j
        bucketTails[bucketIndex] -= 1
        #showSuffixArray(guessedSuffixArray, i)

def isLMSChar(offset, typemap):
    if offset == 0:
        return False
    if typemap[offset] == S_TYPE and typemap[offset - 1] == L_TYPE:
        return True
    return False

def lmsSubstringsAreEqual(string, typemap, offsetA, offsetB):
    if offsetA == len(string) or offsetB == len(string):
        return False
    i = 0
    while True:
        aIsLMS = isLMSChar(i + offsetA, typemap)
        bIsLMS = isLMSChar(i + offsetB, typemap)
        if i > 0 and aIsLMS and bIsLMS:
            return True
        if aIsLMS != bIsLMS:
            return False
        if string[i + offsetA] != string[i + offsetB]:
            return False
        i += 1

def summariseSuffixArray(string, guessedSuffixArray, typemap):
    lmsNames = [-1] * (len(string) + 1)
    currentName = 0
    lastLMSSuffixOffset = None
    lmsNames[guessedSuffixArray[0]] = currentName
    lastLMSSuffixOffset = guessedSuffixArray[0]
    for i in range(1, len(guessedSuffixArray)):
        suffixOffset = guessedSuffixArray[i]
        if not isLMSChar(suffixOffset, typemap):
            continue
        if not lmsSubstringsAreEqual(string, typemap,
                lastLMSSuffixOffset, suffixOffset):
            currentName += 1
        lastLMSSuffixOffset = suffixOffset
        lmsNames[suffixOffset] = currentName
    summarySuffixOffsets = []
    summaryString = []
    for index, name in enumerate(lmsNames):
        if name == -1:
            continue
        summarySuffixOffsets.append(index)
        summaryString.append(name)
    summaryAlphabetSize = currentName + 1
    return summaryString, summaryAlphabetSize, summarySuffixOffsets


def makeSummarySuffixArray(summaryString, summaryAlphabetSize):
    if summaryAlphabetSize == len(summaryString):
        summarySuffixArray = [-1] * (len(summaryString) + 1)
        summarySuffixArray[0] = len(summaryString)
        for x in range(len(summaryString)):
            y = summaryString[x]
            summarySuffixArray[y+1] = x
    else:
        summarySuffixArray = makeSuffixArrayByInducedSorting(summaryString , summaryAlphabetSize,)
    return summarySuffixArray



def accurateLMSSort(string, bucketSizes, typemap, summarySuffixArray, summarySuffixOffsets):
    suffixOffsets = [-1] * (len(string) + 1)
    bucketTails = findBucketTails(bucketSizes)
    for i in range(len(summarySuffixArray)-1, 1, -1):
        stringIndex = summarySuffixOffsets[summarySuffixArray[i]]
        bucketIndex = string[stringIndex]
        suffixOffsets[bucketTails[bucketIndex]] = stringIndex
        bucketTails[bucketIndex] -= 1
        #showSuffixArray(suffixOffsets)
    suffixOffsets[0] = len(string)
    #showSuffixArray(suffixOffsets)
    return suffixOffsets

def makeSuffixArrayByInducedSorting(string, alphabetSize):
    typemap = buildTypeMap(string)
    bucketSizes = findBucketSizes(string, alphabetSize)
    guessedSuffixArray = guessLMSSort(string, bucketSizes, typemap)
    induceSortL(string, guessedSuffixArray, bucketSizes, typemap)
    induceSortS(string, guessedSuffixArray, bucketSizes, typemap)
    summaryString, summaryAlphabetSize, summarySuffixOffsets = \
        summariseSuffixArray(string, guessedSuffixArray, typemap)
    summarySuffixArray = makeSummarySuffixArray(summaryString,summaryAlphabetSize,)
    result = accurateLMSSort(string, bucketSizes, typemap,summarySuffixArray, summarySuffixOffsets)
    induceSortL(string, result, bucketSizes, typemap)
    induceSortS(string, result, bucketSizes, typemap)
    return result


def makeSuffixArray(bytestring):
    return makeSuffixArrayByInducedSorting(bytestring, 256)



def iBWT( S ):
    N = len(S)
    count = [ 0 for _ in range(256)]
    for i in range(N):
        count[S[i]]+=1
    sum = 0
    for i in range(256):
        sum = sum + count[i]
        count[i] = sum - count[i]
    t = [0 for _ in range(256)]
    for i in range(N):
        t[count[S[i]]] = i
        count[S[i]]+=1
    print(t)
    answer = [0 for _ in range(N)]
    j = 1
    for i in range(N):
        answer[i] = S[j]
        j = t[j]
    return answer

def counting_sort_arg(S):
    N = len(S)
    M = 256
    T = [0 for _ in range(M)]
    T_sub = [0 for _ in range(M)]
    for s in S:
        T[s] += 1
    for j in range(1,M):
        T_sub[j] = T_sub[j-1] + T[j-1]
    P = [-1 for _ in range(N)]
    P_inverse = [-1 for _ in range(N)]
    for i in range(N):
        P_inverse[T_sub[S[i]]] = i
        P[i] = T_sub[S[i]]
        T_sub[S[i]] +=1
    return P_inverse

def S_index(S):
    return S.index(0)

def better_iBWT(last_column_BWM, index):
    N = len(last_column_BWM)
    P_inverse = counting_sort_arg(last_column_BWM)
    S = bytearray()
    j = index
    for _ in range(N):
        j = P_inverse[j]
        S.append(last_column_BWM[j])
    return S[:-1]

def make_suffix_array(string,):

    return make_suffix_array_by_induced_sorting(string)


def make_suffix_array_by_induced_sorting(string):
    type_map = build_type_map(string)
    bucket_sizes = find_bucket_sizes(string)
    guessed_suffix_array = guess_lms_sort(string, bucket_sizes, type_map)
    guessed_suffix_array = induce_sort_l(string, guessed_suffix_array, bucket_sizes, type_map)
    guessed_suffix_array = induce_sort_s(string, guessed_suffix_array, bucket_sizes, type_map)
    summary_string, summary_alfabet_size, summary_suffix_indexes = summarise_suffix_array(
        string,  guessed_suffix_array, type_map)
    summary_suffix_array = make_summary_suffix_array(summary_string, summary_alfabet_size)
    result = accurate_lms_sort(
        string,  bucket_sizes, summary_suffix_array, summary_suffix_indexes)
    result = induce_sort_l(string,  result, bucket_sizes, type_map)
    result = induce_sort_s(string,  result, bucket_sizes, type_map)
    return result

# s-type - true, l-type - false
def build_type_map(s, ):
    n = len(s)
    types_of_ch = [False for _ in range(n)]
    for i in range(n - 2, -1, -1):
        if (s[i :(i + 1) ] < s[(i + 1) :(i + 2) ] or
                (s[i :(i + 1) ] == s[(i + 1) :(i + 2) ] and
                 types_of_ch[i + 1])):
            types_of_ch[i] = True
    return types_of_ch


def is_lms_char(index, type_map):
    if index == 0 or index == len(type_map):
        return False
    return type_map[index] and not type_map[index - 1]


def lms_substrings_are_equal(s, type_map, index_a, index_b):
    i = 0
    while True:
        a_is_lms = is_lms_char(i + index_a, type_map)
        b_is_lms = is_lms_char(i + index_b, type_map)
        if i > 0 and a_is_lms and b_is_lms:
            return True
        if (a_is_lms != b_is_lms or i + index_a >= len(type_map) or
                s[(i + index_a) :(i + index_a + 1) ] !=
                s[(i + index_b) :(i + index_b + 1) ]):
            return False
        i += 1


def find_bucket_sizes(string):
    tab = {}
    for i in range(len(string)):
        key = string[i]
        if key in tab:
            tab[key] += 1
        else:
            tab[key] = 1
    return tab


def find_bucket_heads(bucket_sizes):
    index = 0
    res = {}
    for key in sorted(bucket_sizes.keys()):
        res[key] = index
        index += bucket_sizes[key]
    return res


def find_bucket_tails(bucket_sizes):
    index = 0
    res = {}
    for key in sorted(bucket_sizes.keys()):
        index += bucket_sizes[key]
        res[key] = index - 1
    return res


def guess_lms_sort(string, bucket_sizes, type_map):
    n = len(string)
    guessed_suffix_array = [-1] * n
    bucket_tails = find_bucket_tails(bucket_sizes)
    for i in range(n):
        if is_lms_char(i, type_map):
            bucket_index = string[i]
            guessed_suffix_array[bucket_tails[bucket_index]] = i
            bucket_tails[bucket_index] -= 1
    return guessed_suffix_array

def hash_byte (B):
    R = 0
    for _ in B:
        R+= _
    return R

def induce_sort_l(string, guessed_suffix_array, bucket_sizes, type_map):
    if string:
        bucket_heads = find_bucket_heads(bucket_sizes)
        n = len(string)
        j = n - 1
        bucket_index = string[-1:]
        B = hash_byte(bucket_index)
        guessed_suffix_array[ bucket_heads[B]] = j
        bucket_heads[B] += 1
        for i in range(n):
            if guessed_suffix_array[i] != -1:
                j = guessed_suffix_array[i] - 1
                if j >= 0 and not type_map[j]:
                    bucket_index = string[j]
                    guessed_suffix_array[bucket_heads[bucket_index]] = j
                    bucket_heads[bucket_index] += 1
        return guessed_suffix_array
    return []


def induce_sort_s(string, guessed_suffix_array, bucket_sizes, type_map):
    if string:
        n = len(string)
        bucket_tails = find_bucket_tails(bucket_sizes)
        j = n - 1
        if type_map[j]:
            bucket_index = string[-1:]
            guessed_suffix_array[bucket_tails[bucket_index]] = j
            bucket_tails[bucket_index] -= 1
        for i in range(n - 1, -1, -1):
            j = guessed_suffix_array[i] - 1
            if j >= 0 and type_map[j]:
                bucket_index = string[j]
                guessed_suffix_array[bucket_tails[bucket_index]] = j
                bucket_tails[bucket_index] -= 1
        return guessed_suffix_array
    return []


def summarise_suffix_array(string, guessed_suffix_array, type_map):
    n = len(string)
    lms_names = [-1] * n
    current_name = 0
    last_lms_suffix_index = None
    for i in range(n):
        suffix_index = guessed_suffix_array[i]
        if is_lms_char(suffix_index, type_map):
            if not (last_lms_suffix_index is None or
                    lms_substrings_are_equal(
                        string, type_map, last_lms_suffix_index, suffix_index)):
                current_name += 1
            last_lms_suffix_index = suffix_index
            lms_names[suffix_index] = current_name
    summary_suffix_indexes = []
    summary_string = []
    for index, name in enumerate(lms_names):
        if name != -1:
            summary_suffix_indexes.append(index)
            summary_string.append(name)
    summary_alfabet_size = current_name + 1
    return summary_string, summary_alfabet_size, summary_suffix_indexes


def make_summary_suffix_array(summary_string, summary_alfabet_size):
    n = len(summary_string)
    if len(summary_string) == 0 or len(summary_string) == summary_alfabet_size:
        summary_suffix_array = [-1] * n
        for x in range(n):
            y = summary_string[x]
            summary_suffix_array[y] = x
    else:
        summary_suffix_array = make_suffix_array_by_induced_sorting(
            summary_string)
    return summary_suffix_array


def accurate_lms_sort(string, bucket_sizes, summary_suffix_array, summary_suffix_indexes):
    suffix_indexes = [-1] * (len(string))
    bucket_tails = find_bucket_tails(bucket_sizes)
    for i in range(len(summary_suffix_array) - 1, -1, -1):
        string_index = summary_suffix_indexes[summary_suffix_array[i]]
        bucket_index = string[string_index]
        suffix_indexes[bucket_tails[bucket_index]] = string_index
        bucket_tails[bucket_index] -= 1
    return suffix_indexes


def BWT(S):
    S.append(0)
    suffixArray = make_suffix_array(S)
    N = len(S)
    BWT_S = bytearray()
    for i in range(N):
        BWT_S.append(S[suffixArray[i] -1] )
    return BWT_S

