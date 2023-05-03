import argparse
import csv
import sys
import itertools
from datetime import datetime
from io import StringIO
from dgh import CsvDGH
import graph

_DEBUG = True


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

    # ---------------------------BEGINNING---------------------------
    def anonymize(self, qi_names: list, k: int, output_path: str, v=True):

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
            output = open(output_path, 'w')
        except IOError:
            raise

        self.table.seek(0)

        # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
        # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
        # containing the indices of the rows in the original table file with those QI values:
        qi_frequency = dict()  # K = Tuple ("a","b","c") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

        # List of Tuples that will save the state of the table at specific generalization levels
        # Will be needed to reset the Table to a desirable state while generalizing by following combinations
        qi_frequency_states = dict()  # Es. [0] = 000; [1] = xx0; [2] = x00

        # List of dictionaries where every iteration of the modified tables will be saved
        qi_frequency_candidates = dict()  # K = Tuple ("a","b","c"), V = qi_frequency related to the combination in K

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # the current levels of generalization, from 0 (not generalized):
        gen_levels = dict()
        for i, attribute in enumerate(qi_names):
            gen_levels[i] = 0

        # Initialize qi_frequency
        for i, row in enumerate(self.table):
            # i = index row
            # row value
            qi_sequence = self._get_values(row, qi_names, i)  # list of values contained in qi_names at row 'i'

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

        # ---------------------------START PART 1 - Generalization---------------------------

        # GET HEIGHTS OF QI
        qi_heights = list()

        for i in qi_names:
            tmp = list()
            for n in range(CsvDGH.get_tree_height(table.dghs[i]) + 1):
                tmp.append(n)
            qi_heights.append(tmp)

        heights = dict()
        h = 0
        for hi in qi_names:
            heights[hi] = qi_heights[h]
            h = h+1

        #print(heights)
        #print(len(qi_names))
        count = 1
        while count < len(qi_names)+1:
            if count == 1:
                # roba Giam
                #
                count = count+1
            else:
                listofcomb = list(itertools.combinations(qi_names, count))
                print(listofcomb)
                comb = 0
                while comb < len(listofcomb):
                    heightxcomb = list()
                    for hi in list(listofcomb[comb]):
                        #print(heights[hi])
                        heightxcomb.append(heights[hi])
                    print(heightxcomb)
                    G = graph.MyDiGraph()
                    G.add_vertices(heightxcomb, listofcomb[comb])
                    G.add_linked_edge(listofcomb[comb])
                    #print(G.getEdges())
                    #print(G.nodes)
                    comb = comb + 1




                count = count+1



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

    # ---------------------------END PART2 - Write on output file---------------------------

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
