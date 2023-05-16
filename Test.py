import csv
import sys
from io import StringIO
import graph
import parsing
from dgh import CsvDGH
import copy
import itertools


class _Table:

    def __init__(self, pt_path: str, dgh_paths: dict):

        """
        Instantiates a table and the specified Domain Generalization Hierarchies from the
        corresponding files.

        :param pt_path:             Path to the table to anonymize.
        :param dgh_paths:           Dictionary whose values are paths to DGH files and whose keys
                                    are the corresponding attribute names.
        :raises IOError:            If a file cannot be read.
        :raises FileNotFoundError:  If a file cannot be found.
        """

        self.table = None
        """
        Reference to the table file.
        """
        self.attributes = dict()
        """
        Dictionary whose keys are the table attributes names and whose values are the corresponding
        column indices.
        """
        self._init_table(pt_path)
        """
        Reference to the table file.
        """
        self.dghs = dict()
        """
        Dictionary whose values are DGH instances and whose keys are the corresponding attribute 
        names.
        """
        for attribute in dgh_paths:
            self._add_dgh(dgh_paths[attribute], attribute)

    def __del__(self):

        """
        Closes the table file.
        """

        self.table.close()

    @staticmethod
    def _log(content, enabled=True, endl=True):

        """
        Prints a log message.

        :param content: Content of the message.
        :param enabled: If False the message is not printed.
        """

        if enabled:
            if endl:
                print(content)
            else:
                sys.stdout.write('\r' + content)

    @staticmethod
    def _debug(content, enabled=False):

        """
        Prints a debug message.

        :param content: Content of the message.
        :param enabled: If False the message is not printed.
        """

        if enabled:
            print(content)

    def _init_table(self, pt_path: str):

        """
        Gets a reference to the table file and instantiates the attribute dictionary.

        :param pt_path:             Path to the table file.
        :raises IOError:            If the file cannot be read.
        :raises FileNotFoundError:  If the file cannot be found.
        """

        try:
            self.table = open(pt_path, 'r')
        except FileNotFoundError:
            raise

    def _get_values(self, row: str, attributes: list, row_index=None):

        """
        Gets the values corresponding to the given attributes from a row.

        :param row:         Line of the table file.
        :param attributes:  Names of the attributes to get the data of.
        :param row_index:   Index of the row in the table file.
        :return:            List of corresponding values if valid, None if this row must be ignored.
        :raises KeyError:   If an attribute name is not valid.
        :raises IOError:    If the row cannot be read.
        """

        # Ignore empty lines:
        if row.strip() == '':
            return None

    def _set_values(self, row, values, attributes: list) -> str:

        """
        Sets the values of a row for the given attributes and returns the row as a formatted string.

        :param row:         List of values of the row.
        :param values:      Values to set.
        :param attributes:  Names of the attributes to set.
        :return:            The new row as a formatted string.
        """

        pass

    def _add_dgh(self, dgh_path: str, attribute: str):

        """
        Adds a Domain Generalization Hierarchy to this table DGH collection, from its file.

        :param dgh_path:            Path to the DGH file.
        :param attribute:           Name of the attribute with this DGH.
        :raises IOError:            If the file cannot be read.
        :raises FileNotFoundError:  If the file cannot be found.
        """

        pass


class CsvTable(_Table):

    def __init__(self, pt_path: str, dgh_paths: dict):

        super().__init__(pt_path, dgh_paths)

    def __del__(self):

        super().__del__()

    def anonymize(self, qi_names, k, output_path, v=False):

        super().anonymize(qi_names, k, output_path, v)

    def _init_table(self, pt_path):

        super()._init_table(pt_path)

        try:
            # Try to read the first line (which contains the attribute names):
            csv_reader = csv.reader(StringIO(next(self.table)))
        except IOError:
            raise

        # Initialize the dictionary of table attributes:
        for i, attribute in enumerate(next(csv_reader)):
            self.attributes[attribute] = i

    def _get_values(self, row: str, attributes: list, row_index=None):

        super()._get_values(row, attributes, row_index)

        # Ignore the first line (which contains the attribute names):
        if row_index is not None and row_index == 0:
            return None

        # Try to parse the row:
        try:
            csv_reader = csv.reader(StringIO(row))
        except IOError:
            raise
        parsed_row = next(csv_reader)

        values = list()
        for attribute in attributes:
            if attribute in self.attributes:
                values.append(parsed_row[self.attributes[attribute]])
            else:
                raise KeyError(attribute)

        return values

    def _set_values(self, row: list, values, attributes: list):

        for i, attribute in enumerate(attributes):
            row[self.attributes[attribute]] = values[i]

        values = StringIO()
        csv_writer = csv.writer(values)
        csv_writer.writerow(row)

        return values.getvalue()

    def _add_dgh(self, dgh_path, attribute):

        try:
            self.dghs[attribute] = CsvDGH(dgh_path)
        except FileNotFoundError:
            raise
        except IOError:
            raise

    # ---------------------------BEGINNING---------------------------
    def anonymize(self, qi_names: list, k: int, output: str, v=True):

        """
            Writes a k-anonymous representation of this table on a new file. The maximum number of
            suppressed rows is k.

            :param qi_names:    List of names of the Quasi Identifiers attributes to consider during
                                k-anonymization.
            :param k:           Level of anonymity.
            :param output_path: Path to the output file.
            :param v:           If True prints some logging.
            :raises KeyError:   If a QI attribute name is not valid.
            :raises IOError:    If the output file cannot be written.
            """

        '''try:
                output = open(output_path, 'w')
            except IOError:
                raise'''

        print("Start Anon")

        self.table.seek(0)

        # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
        # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
        # containing the indices of the rows in the original table file with those QI values:
        qi_frequency = dict()  # K = Tuple ("a","b","c") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # the current levels of generalization, from 0 (not generalized):
        gen_levels = dict()

        k_anon_queue = dict()

        qi_frequency = generate_frequency(self, qi_names)

        # ---------------------------START PART 1 - Generalization---------------------------
        # GET HEIGHTS OF QI
        qi_heights = list()

        for qi in qi_names:
            tmp = list()
            for n in range(CsvDGH.get_tree_height(table.dghs[qi]) + 1):
                tmp.append(n)
            qi_heights.append(tmp)

        heights = dict()
        h = 0
        for hi in qi_names:
            heights[hi] = qi_heights[h]
            h = h + 1
        # call the function mono and multi
        mono_attr_verify(self, qi_names, qi_heights, k, table.dghs, k_anon_queue)
        multi_attr_verify(qi_names, heights, k_anon_queue)

        # ---------------------------START PART 2 - Write on output file---------------------------

        self._debug("[DEBUG] Suppressing max k non k-anonymous tuples...")
        # Drop tuples which occur less than k times:
        '''for qi_sequence, data in qi_frequency.items():
                if data[0] < k:
                    qi_frequency.pop(qi_sequence)'''

        # Start to read the table file from the start:
        self.table.seek(0)

        for i, row in enumerate(self.table):

            table_row = self._get_values(row, list(self.attributes), i)

            # Skip this row if it must be ignored:
            if table_row is None:
                continue

            # Find sequence corresponding to this row index:
            for qi_sequence in qi_frequency:
                if i in qi_frequency[qi_sequence][1]:  # if index row is in the set of indexes
                    line = self._set_values(table_row, qi_sequence, qi_names)
                    print(line, file=output, end="")
                    break

        output.close()


# :param table: table to check anonymization
# :param k: level of anonymization
# check if table is k-anon
# meaning check if there are less than k sequences that have a repetition lower than k
def is_k_anon(table, k):
    count = 0  # non k-anon touples count
    for key in table:
        if table[key][0] < k:
            count += table[key][0]
    return count <= k


def generate_frequency(csvtable, qi_names):
    # print("ENTER gen_freq")
    # print("Names given: ",qi_names)
    csvtable.table.seek(0)
    qi_frequency = dict()
    # Initialize qi_frequency
    for i, row in enumerate(csvtable.table):
        # i = index row
        # row value
        qi_sequence = csvtable._get_values(row, qi_names, i)  # list of values contained in qi_names at row 'i'

        # Skip if this row must be ignored:
        if qi_sequence is not None:
            qi_sequence = tuple(qi_sequence)  # list -> tuple ("val_a","val_b","val_c")

        if qi_sequence in qi_frequency:  # if qi_val_combination in qi_frequency Key
            occurrences = qi_frequency[qi_sequence][0] + 1  # add occurence of qi_sequence
            rows_set = qi_frequency[qi_sequence][1].union([i])  # add index
            qi_frequency[qi_sequence] = (occurrences, rows_set)  # update value
        else:
            # Initialize number of occurrences and set of row indices:
            qi_frequency[qi_sequence] = (1, set())
            qi_frequency[qi_sequence][1].add(i)
    # print("END gen_freq, qi_freq result: ",qi_frequency)
    return qi_frequency


# TODO: INPUT QUEUE FROM OUTSIDE
def mono_attr_verify(csvtable, qi_names, qi_heights, k, dghs, k_anon_queue):

    count = 1
    while count<len(qi_names):
        # print("Enter Mono\n")
        # print("current k:",k)

        listofcomb = list(itertools.combinations(qi_names, count))

        # vertex text format "qi_name1 : lv1 ; qi_name2 : lv2 ;..."
        comb = 0
        while comb < len(listofcomb):

            heightxcomb = list()
            qinamesxcomb = list()

            for hi in list(listofcomb[comb]):
                qinamesxcomb.append(hi)
                heightxcomb.append(qi_heights[hi])
            # if elementi misti if count >1
            if count > 1:
                if (count -1) not in k_anon_queue:
                    notfound = True
                else:
                    notfound = False

            # print("\nCurrent QI: ",qi_names[i])
            qi_frequency = generate_frequency(csvtable, qinamesxcomb)

            G = graph.MyDiGraph()
            G.add_vertices(heightxcomb, listofcomb[comb])
            G.add_linked_edge(qinamesxcomb)

            queue_node = [G.getRoots()]

            while True:
                current = queue_node.pop(0)

                # TODO searchimg as in the monodimensionality check
                to_ignore = False
                if count > 1 or notfound == False:
                    to_ignore = True
                    comb_current = current.split(";")
                    list_comb_to_check = list(itertools.combinations(comb_current, count - 1))
                    for c in list_comb_to_check:
                        if c in k_anon_queue[count - 1]:
                            to_ignore = False
                            break
                if to_ignore == False or count == 1:

                    if not G.isMarked(current):

                        if is_k_anon(generalize(qinamesxcomb, dghs, qi_frequency, heightxcomb), k):
                            k_anon_queue[count].append(current)
                            G.setMarked(current)
                            if G.getChildren(current):
                                for n in G.getChildren(current):
                                    G.setMarked(n)
                                    G.setHereditary(n)
                    else:
                        k_anon_queue[count].append(current)

                # break the loop
                if not G.getChildren(current):
                    break

                for n in G.getChildren(current):
                    if n in queue_node:
                        continue
                    queue_node.append(n)
            comb = comb + 1
        count = count + 1

    return


# TODO: Verify which steps and functions are needed in order to achieve this funtion
def multi_attr_verify(qi_names, heights, k_anon_queue):
    count = len(k_anon_queue) + 1
    while count <= len(qi_names):
        listofcomb = list(itertools.combinations(qi_names, count))
        comb = 0

        while comb < len(listofcomb):

            heightxcomb = list()
            qinamesxcomb = list()

            for hi in list(listofcomb[comb]):
                qinamesxcomb.append(hi)
                heightxcomb.append(heights[hi])
            G = graph.MyDiGraph()
            G.add_vertices(heightxcomb, listofcomb[comb])
            G.add_linked_edge(qinamesxcomb)

            # Search BFS bottom top
            queue_node = [G.getRoots()]

            while True:

                current = queue_node.pop(0)

                # Check anonymity

                queue_k_anon = dict()
                # [1: ('sex:2')
                # 2: ('sex:2;age:4')
                # 3: (('sex:2;age:4;zipcode:1'),.....)
                # .
                # .
                # .]

                comb_current = current.split(";")
                list_comb_to_check = list(itertools.combinations(comb_current, count - 1))
                is_k = True

                for c in list_comb_to_check:
                    if not c in queue_k_anon[count - 1]:
                        is_k = False
                        break
                if is_k:
                    queue_k_anon[count].append(current)

                # break the loop
                if not G.getChildren(current):
                    break

                for n in G.getChildren(current):
                    if n in queue_node:
                        continue
                    queue_node.append(n)

                print("current queue: ", queue_node, "\n")

            comb = comb + 1
        count = count + 1
    return


# TODO: CHANGE DIMENSION OF QI_NAMES TO CHECK SINGLE ATTRIBUTE
# data contains the generalization levels -> combination to generalize to
def generalize(qi_names, dghs, og_frequency, *data):
    # print("\nEnter Gen")
    # print("Current <COMB>: ", data)

    if all(n == 0 for n in data):
        return copy.copy(og_frequency)

    qi_frequency = copy.copy(og_frequency)  # shallow copy

    # Look up table for the generalized values, to avoid searching in hierarchies:
    generalizations = dict()
    # Generalized value to apply for the needed labels
    generalized_value = dict()
    # Note: using the list of keys since the dictionary is changed in size at runtime
    # and it can't be used as an iterator:
    for j, qi_sequence in enumerate(list(qi_frequency)):
        # print("Current J: ",j)
        if j == 0: continue
        # Get the generalized value:
        for i in range(len(data)):
            # If QI is going back to genLv 0 then do nothing since it has already been "rolled back" with resetState
            # If old and new level are the same then do nothing once again
            # print(data[i])
            if data[i] != 0:
                if qi_sequence[i] in generalizations:
                    # Find directly the generalized value in the look up table:
                    generalized_value[i] = generalizations[i]
                else:
                    # Get the corresponding generalized value from the attribute DGH:
                    try:
                        # print("Enter Generalized_Jump")
                        # print("Current i: ", i, "; Current qi_names[i]", qi_names[i])
                        # print("data: ",data)
                        # print("qi_names: ",qi_names)
                        # print("Current i: ", i)
                        # print("qi_sequence[i] = ",qi_sequence[i])
                        generalized_value[i] = dghs[qi_names[i]] \
                            .generalize_jump(
                            qi_sequence[i], 0,
                            data[i])
                        # print("Exit Generalized_Jump")
                    except KeyError as error:
                        # print("Error: ",error)
                        return
                    if generalized_value[i] is None:
                        # Skip if it's a hierarchy root:
                        continue

                # Add to the look-up table:
                generalizations[i] = generalized_value[i]

        # Skip if header of Table
        if qi_sequence is None: continue

        # Tuple with generalized value:
        new_qi_sequence = list(qi_sequence)
        # Change only the attributes that need to be changed -> the ones with a generalization level different from before
        for id, gen_val in generalized_value.items():
            new_qi_sequence[id] = gen_val
        new_qi_sequence = tuple(new_qi_sequence)

        # If start of cycle no need to change or apply anything
        # Check if there is already a tuple like this one:
        if new_qi_sequence in qi_frequency:
            # Update the already existing one:
            # Update the number of occurrences:
            occurrences = qi_frequency[new_qi_sequence][0] \
                          + qi_frequency[qi_sequence][0]
            # Unite the row indices sets:
            rows_set = qi_frequency[new_qi_sequence][1] \
                .union(qi_frequency[qi_sequence][1])
            qi_frequency[new_qi_sequence] = (occurrences, rows_set)
            # Remove the old sequence:
            qi_frequency.pop(qi_sequence)
        else:
            # Add new tuple and remove the old one:
            qi_frequency[new_qi_sequence] = qi_frequency.pop(qi_sequence)

    # print("Res qi_frequency: ",qi_frequency)
    return qi_frequency


if __name__ == "__main__":

    dgh_paths = dict()

    table_path = "/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/db_200.csv"

    k = 2

    qis = ("age", "sex", "zip_code")

    gen_paths = list()
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/age_generalization.csv")
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/sex_generalization.csv")
    gen_paths.append("/home/novi/Documents/Uni/Year3/IDS/workspace/DP-Project6/tables/zip_code_generalization.csv")

    for i, qi_name in enumerate(qis):
        dgh_paths[qi_name] = gen_paths[i]
    table = CsvTable(table_path, dgh_paths)

    try:
        table.anonymize(qis, k)
    except KeyError as error:
        if len(error.args) > 0:
            print("[ERROR] Quasi Identifier", error.args[0], "is not valid.")
        else:
            print("[ERROR] A Quasi Identifier is not valid.")
    '''try:
        res = table.anonymize(qis, k)
    except KeyError as error:
        if len(error.args) > 0:
            print("[ERROR] Quasi Identifier",error.args[0],"is not valid.")
        else:
            print("[ERROR] A Quasi Identifier is not valid.")

    #print(datafly.is_k_anon(res, k))
    #print(datafly.suppress_under_k(res,k))

    for key in res:
        print("Key: ",key,"; Reps: ",res[key][0],", Set of rows: ", res[key][1])'''

    '''qi_heights = list()

    #CsvDGH.getTreeHeight(table.dghs[qis[0]])

    print(CsvDGH.get_tree_height(table.dghs[qis[0]]))

    #print(table.dghs[qis[0]].hierarchies['0-50'].root.children['0-20'].children['0-10'].children['1'].children)

    heights = list()
    for i in qis:
        tmp = list()
        for n in range(CsvDGH.get_tree_height(table.dghs[i])+1):
            tmp.append(n)
        qi_heights.append(tmp)

    print(qi_heights)

    #qi_heights = [[0, 1, 2, 3], [0, 1], [0, 1, 2, 3, 4, 5]]

    # create QI_Combination list to follow
    combinations = datafly.combination(*qi_heights)

    print(combinations)
'''
