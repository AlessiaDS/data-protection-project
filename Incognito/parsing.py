import itertools


def parse_attr(st):
    comb = {}
    levels = st.split(";")
    for level in levels:
        qi_l = level.split(":")
        comb[qi_l[0]] = qi_l[1]
    return comb


def reparse_attr(dict_attr):
    string_attr = ""
    for k in dict_attr.keys():
        temp_str = string_attr
        string_attr = temp_str + str(k) + ":" + str(dict_attr[k]) + ";"
        final_string_attr = string_attr[:-1]
    return final_string_attr


def parse_multi(list_c):
    new_qi_list = list()
    for c in list_c:
        string_attr = ""
        q = 0
        while q < len(c):
            str_tmp = c[q]
            temp_str = string_attr
            string_attr = temp_str + str_tmp + ";"
            q = q + 1
        final_string_attr = string_attr[:-1]
        print(final_string_attr)

        new_qi_list.append(final_string_attr)
    list_c = new_qi_list
    return list_c


if __name__ == "__main__":
    current = 'sex:2;age:4;zipcode:1'
    comb_current = current.split(";")
    print(comb_current)
    list_comb_to_check = list(itertools.combinations(comb_current, 2))
    print(list_comb_to_check)
    list_comb_to_check = parse_multi(list_comb_to_check)
    print(list_comb_to_check)
