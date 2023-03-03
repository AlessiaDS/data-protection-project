import sys


def findMin(qi_seq):
    gen_min = [sys.maxsize, None]
    for k, v in qi_seq:
        weight = sum(k)
        if weight < gen_min[0]:
            gen_min[0] = weight
            gen_min[1] = v
        return gen_min


