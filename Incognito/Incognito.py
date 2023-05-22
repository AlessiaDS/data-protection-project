import csv
import sys
from io import StringIO
import graph
import parsing
from dgh import CsvDGH
import copy
import itertools
from datetime import datetime
import argparse


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

        try:
            output = open(output, 'w')
        except IOError:
            raise

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
        mono_attr_verify(self, qi_names, heights, k, table.dghs, k_anon_queue)
        print('change')
        print(k_anon_queue)
        multi_attr_verify(qi_names, heights, k_anon_queue)

        qi_frequency = find_min(k_anon_queue, qi_names, qi_frequency, table.dghs)

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


# TODO: find min of generalization
def mono_attr_verify(csvtable, qi_names, qi_heights, k, dghs, k_anon_queue):
    """
            Anonimyze monodimensional graph and eventually n-dimensional ones.

            :param cvstable:            Path to the table to anonymize.
            :param qi_names:            List whose values are names of QI
            :param qi_heights:          Dictionary containing the heights of every QI, in a range format.
            :param k:                   Level of anonymity.
            :param dghs:                Dictionary whose values are paths to DGH files and whose keys
                                        are the corresponding attribute names.
            :param k_anon_queue:        Dictionary containing the k anonymous combination each n-dimensions.
            """
    print(qi_heights)
    count = 1

    while count <= len(qi_names):
        # k_anon_queue[count] = list()
        listofcomb = list(itertools.combinations(qi_names, count))
        # print("Current size of Vertices",count)

        # vertex text format "qi_name1 : lv1 ; qi_name2 : lv2 ;..."
        comb = 0
        notfound = True
        found_k_anon = False

        while comb < len(listofcomb):
            # print(comb,"indice")
            found_k_anon = False
            heightxcomb = list()
            qinamesxcomb = list()

            for hi in list(listofcomb[comb]):
                qinamesxcomb.append(hi)
                heightxcomb.append(qi_heights[hi])
            if count > 1:
                if (count - 1) not in k_anon_queue:
                    notfound = True
                else:
                    notfound = False

            # print("\nCurrent QI: ",qi_names[i])
            qi_frequency = generate_frequency(csvtable, qinamesxcomb)

            G = graph.MyDiGraph()
            G.add_vertices(heightxcomb, listofcomb[comb])
            G.add_linked_edge(qinamesxcomb)
            # G.printOut()
            queue_node = G.getRoots()

            while True:
                current = queue_node.pop(0)
                # current = current[0]
                print("Current Vertex: ", current)
                to_ignore = False
                if count > 1 or notfound == False:
                    to_ignore = True
                    comb_current = current.split(";")
                    list_comb_to_check = list(itertools.combinations(comb_current, count - 1))
                    list_comb_to_check = parsing.parse_multi(list_comb_to_check)
                    # print("content to check",list_comb_to_check)
                    for c in list_comb_to_check:
                        print("Selected queue: ", k_anon_queue[count - 1])
                        if c in k_anon_queue[count - 1]:
                            print(" k anon comb", c)
                            to_ignore = False
                            break
                if to_ignore == False or count == 1:
                    # print("Should be here")
                    # print('ok', G.isMarked(current))
                    if not G.isMarked(current):
                        # print("entered")
                        data = tuple()
                        tmp = parsing.parse_attr(current)
                        # print(tmp)

                        for i in tmp:
                            data = data + (int(tmp[i]),)

                        # print("Content of freq", qi_frequency)

                        # print("Data",data)
                        # print("Content of k_anon_queue: ",k_anon_queue)
                        print("Generalized table: ", generalize(qinamesxcomb, dghs, qi_frequency, *data))
                        if is_k_anon(generalize(qinamesxcomb, dghs, qi_frequency, *data), k):
                            # print(generalize(qinamesxcomb, dghs, qi_frequency, *data))
                            found_k_anon = True
                            print(current, "is K-Anon")
                            if k_anon_queue.get(count):  # "None" is counted as "False"
                                k_anon_queue[count].append(current)
                            else:
                                k_anon_queue[count] = [current]
                            # print(k_anon_queue)
                            G.setMarked(current)
                            if G.getChildren(current):
                                for n in G.getChildren(current):
                                    G.setMarked(n)
                                    G.setHereditary(n)

                    else:
                        print(current, "is K-Anon")
                        k_anon_queue[count].append(current)

                # break the loop
                if not G.getChildren(current):
                    break

                for n in G.getChildren(current):
                    if n in queue_node:
                        continue
                    queue_node.append(n)

            comb = comb + 1

        if found_k_anon:
            print('esc')
            return

        count = count + 1

    return


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
            queue_node = G.getRoots()

            while True:

                current = str(queue_node.pop(0))
                print("Current Index: ", current)

                # Check anonymity

                # [1: ('sex:2')
                # 2: ('sex:2;age:4')
                # 3: (('sex:2;age:4;zipcode:1'),.....)
                # .
                # .
                # .]

                comb_current = current.split(";")
                # print(comb_current)
                list_comb_to_check = list(itertools.combinations(comb_current, count - 1))
                list_comb_to_check = parsing.parse_multi(list_comb_to_check)
                # [('age:0', 'sex:0'), ('age:0', 'zip_code:0'), ('sex:0', 'zip_code:0')] at count =3
                print(list_comb_to_check)
                is_k = True

                for c in list_comb_to_check:
                    # print("current element: ", c[0])

                    if c not in k_anon_queue[count - 1]:
                        is_k = False
                if is_k:

                    print('entered')
                    if k_anon_queue.get(count):  # "None" is counted as "False"
                        k_anon_queue[count].append(current)
                    else:
                        k_anon_queue[count] = [current]

                # break the loop
                if not G.getChildren(current):
                    break

                for n in G.getChildren(current):
                    if n in queue_node:
                        continue
                    queue_node.append(n)

                # print("current queue: ", queue_node, "\n")
            comb = comb + 1

        count = count + 1
    return print(k_anon_queue)


# data contains the generalization levels -> combination to generalize to
def generalize(qi_names, dghs, og_frequency, *data):
    # print("\nEnter Gen")
    # print("Current <COMB>: ", data)

    if all(n == 0 for n in data):
        # print("Current qi_names: ", qi_names)
        # print("Res qi_frequency: ", og_frequency)
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

    # print("Current qi_names: ", qi_names)
    # print("Res qi_frequency: ",qi_frequency)
    return qi_frequency


def find_min(k_anon_queue, qi_names, qi_frequency, dghs):
    min = k_anon_queue[len(qi_names)][0]
    tmp = parsing.parse_attr(min)
    data = tuple()

    for i in tmp:
        data = data + (int(tmp[i]),)

    qi_frequency = generalize(qi_names, dghs, qi_frequency, *data)

    return qi_frequency


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Python implementation of the Datafly algorithm. Finds a k-anonymous "
                    "representation of a table.")
    parser.add_argument("--private_table", "-pt", required=True,
                        type=str, help="Path to the CSV table to K-anonymize.")
    parser.add_argument("--quasi_identifier", "-qi", required=True,
                        type=str, help="Names of the attributes which are Quasi Identifiers.",
                        nargs='+')
    parser.add_argument("--domain_gen_hierarchies", "-dgh", required=True,
                        type=str, help="Paths to the generalization files (must have same order as "
                                       "the QI name list.",
                        nargs='+')
    parser.add_argument("-k", required=True,
                        type=int, help="Value of K.")
    parser.add_argument("--output", "-o", required=True,
                        type=str, help="Path to the output file.")
    args = parser.parse_args()

    try:

        start = datetime.now()

        dgh_paths = dict()
        for i, qi_name in enumerate(args.quasi_identifier):
            dgh_paths[qi_name] = args.domain_gen_hierarchies[i]
        table = CsvTable(args.private_table, dgh_paths)
        try:
            table.anonymize(args.quasi_identifier, args.k, args.output, v=True)
        except KeyError as error:
            if len(error.args) > 0:
                _Table._log("[ERROR] Quasi Identifier '%s' is not valid." % error.args[0],
                            endl=True, enabled=True)
            else:
                _Table._log("[ERROR] A Quasi Identifier is not valid.", endl=True, enabled=True)

        end = (datetime.now() - start).total_seconds()
        _Table._log("[LOG] Done in %.2f seconds (%.3f minutes (%.2f hours))" %
                    (end, end / 60, end / 60 / 60), endl=True, enabled=True)

    except FileNotFoundError as error:
        _Table._log("[ERROR] File '%s' has not been found." % error.filename,
                    endl=True, enabled=True)
    except IOError as error:
        _Table._log("[ERROR] There has been an error with reading file '%s'." % error.filename,
                    endl=True, enabled=True)
