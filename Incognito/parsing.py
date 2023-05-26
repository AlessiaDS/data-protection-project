def parse_attr(st):
    """
    Function to parse a string containing the combination of QI into a dictionary
    :param st:                  string containing the QI combination in the following format:
                                "qi1 : lv ; qi2 : lv; ..."
    :return:                    dictionary containing the QI and their generalization levels in the following format:
                                {st: {"qi1": lv, "qi2": lv ..}}
    """
    comb = {}
    levels = st.split(";")
    for level in levels:
        qi_l = level.split(":")
        comb[qi_l[0]] = qi_l[1]
    return comb


def reparse_attr(dict_attr):
    """
    Function to parse a dictionary containing the combination of QI into a string
    :param dict_attr:           dictionary containing the QI and their generalization levels in the following format:
                                {"qi1": lv, "qi2": lv ..}
    :return:                    string containing the QI combination in the following format:
                                "qi1 : lv ; qi2 : lv; ..."
    """
    string_attr = ""
    for k in dict_attr.keys():
        temp_str = string_attr
        string_attr = temp_str + str(k) + ":" + str(dict_attr[k]) + ";"
        final_string_attr = string_attr[:-1]
    return final_string_attr


def parse_multi(list_c):
    """
    Function used to join element of a list containing the QI combination into one string

    :param list_c:              list of combinations in the following format:
                                (("qi1 : lv" , "qi2: lv"), ...)

    :return:                    list of combinations in the following format:
                                (("qi1 : lv ; qi2: lv;..."), ...)
    """
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
        new_qi_list.append(final_string_attr)
    list_c = new_qi_list
    return list_c
