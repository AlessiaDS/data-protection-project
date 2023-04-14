
def parse_attr(st):
    comb = {}
    levels = st.split(";")
    for level in levels:
        qi_l = level.split(":")
        # meglio una tupla
        comb[qi_l[0]] = qi_l[1]
    return comb


def reparse_attr(dict_attr):
    string_attr = ""
    for k in dict_attr.keys():
        temp_str = string_attr
        string_attr = temp_str + str(k) + ":" + str(dict_attr[k]) + ";"
        final_string_attr = string_attr[:-1]
    return final_string_attr


#parsimg inverso per ricavare la nuova combinazione
#aggiungo edge incrementando e cercando nellla lista di vertici il corrisoondente
