# Incognito k-Anonymization algorithm as defined by LeFevre

import networkx as nx
from collections import OrderedDict
import argparse
from datetime import datetime



class Incognito:

    def __init__(self, table):
        self.quasi_combination_list = list()
        self.G = nx.Graph #rifare
        self.list_of_kAnon = list()
        self.rAttributeGen = OrderedDict()  # EQUIVALENT LinkedHashMap<String, Graph>
        self.table = table

    def getQuasiCombinations(self, table, r):
        quasi_id_list = list()
        quasi_id_list.append(self.table.get_quasi_id().get_data())
        quasi_id = np.array(input
        combination(quasi_id, new String[quasiIden.size()], 0, quasiIden.size() - 1, 0, r);

    def mainIncognitoAlgorithm(self, k):

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Python implementation of the  algorithm. Finds a k-anonymous "
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
        start = datetime.now()  # used for statistics
        dgh_paths = dict()
        for i, qi_name in enumerate(args.quasi_identifier):
            dgh_paths[qi_name] = args.domain_gen_hierarchies[i]
        self.table = datafly.CsvTable(args.private_table, dgh_paths)
        try:
            mainIncognitoAlgorithm(args.k);

        end = (datetime.now() - start).total_seconds()










###################################################################################################

        except KeyError as error:
            if len(error.args) > 0:
                datafly._Table._log("[ERROR] Quasi Identifier '%s' is not valid." % error.args[0],
                                    endl=True, enabled=True)
            else:
                datafly._Table._log("[ERROR] A Quasi Identifier is not valid.", endl=True, enabled=True)

        end = (datetime.now() - start).total_seconds()
        datafly._Table._log("[LOG] Done in %.2f seconds (%.3f minutes (%.2f hours))" %
                            (end, end / 60, end / 60 / 60), endl=True, enabled=True)

    except FileNotFoundError as error:
        datafly._Table._log("[ERROR] File '%s' has not been found." % error.filename,
                            endl=True, enabled=True)
    except IOError as error:
        datafly._Table._log("[ERROR] There has been an error with reading file '%s'." % error.filename,
                            endl=True, enabled=True)

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

        global _DEBUG

        try:
            output = open(output_path, 'w')
        except IOError:
            raise

        # Start reading the table file from the top:
        self.table.seek(0)

        # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
        # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
        # containing the indices of the rows in the original table file with those QI values:
        qi_frequency = dict()

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # sets containing the corresponding domain elements:
        domains = dict()
        for i, attribute in enumerate(qi_names):
            domains[i] = set()

        # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
        # the current levels of generalization, from 0 (not generalized):
        gen_levels = dict()
        for i, attribute in enumerate(qi_names):
            gen_levels[i] = 0

        for i, row in enumerate(self.table):
            # i = index row
            # row value
            qi_sequence = self._get_values(row, qi_names, i)

            # Skip if this row must be ignored:
            if qi_sequence is None:
                continue
            else:
                qi_sequence = tuple(qi_sequence)

            if qi_sequence in qi_frequency:
                occurrences = qi_frequency[qi_sequence][0] + 1  # add occurence of qi_sequence
                rows_set = qi_frequency[qi_sequence][1].union([i])  # add index
                qi_frequency[qi_sequence] = (occurrences, rows_set)  # update value
            else:
                # Initialize number of occurrences and set of row indices:
                qi_frequency[qi_sequence] = (1, set())
                qi_frequency[qi_sequence][1].add(i)

                # Update domain set for each attribute in this sequence:
                for j, value in enumerate(qi_sequence):
                    domains[j].add(value)

        while True:

            # Number of tuples which are not k-anonymous.
            count = 0

            for qi_sequence in qi_frequency:

                # Check number of occurrences of this sequence:
                if qi_frequency[qi_sequence][0] < k:
                    # Update the number of tuples which are not k-anonymous:
                    count += qi_frequency[qi_sequence][0]

            # Limit the number of tuples to suppress to k:
            if count > k:

                # Get the attribute whose domain has the max cardinality:
                max_cardinality, max_attribute_idx = 0, None
                for attribute_idx in domains:
                    if len(domains[attribute_idx]) > max_cardinality:
                        max_cardinality = len(domains[attribute_idx])
                        max_attribute_idx = attribute_idx

                # Index of the attribute to generalize:
                attribute_idx = max_attribute_idx

                # Generalize each value for that attribute and update the attribute set in the
                # domains dictionary:
                domains[attribute_idx] = set()
                # Look up table for the generalized values, to avoid searching in hierarchies:
                generalizations = dict()

                # Note: using the list of keys since the dictionary is changed in size at runtime
                # and it can't be used an iterator:
                for j, qi_sequence in enumerate(list(qi_frequency)):

                    # Get the generalized value:
                    if qi_sequence[attribute_idx] in generalizations:
                        # Find directly the generalized value in the look up table:
                        generalized_value = generalizations[attribute_idx]
                    else:
                        # Get the corresponding generalized value from the attribute DGH:
                        try:
                            generalized_value = self.dghs[qi_names[attribute_idx]] \
                                .generalize(
                                qi_sequence[attribute_idx],
                                gen_levels[attribute_idx])
                        except KeyError as error:
                            output.close()
                            return

                        if generalized_value is None:
                            # Skip if it's a hierarchy root:
                            continue

                        # Add to the look up table:
                        generalizations[attribute_idx] = generalized_value

                    # Tuple with generalized value:
                    new_qi_sequence = list(qi_sequence)
                    new_qi_sequence[attribute_idx] = generalized_value
                    new_qi_sequence = tuple(new_qi_sequence)

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

                    # Update domain set with this attribute value:
                    domains[attribute_idx].add(qi_sequence[attribute_idx])

                # Update current level of generalization:
                gen_levels[attribute_idx] += 1

            else:

                # Drop tuples which occur less than k times:
                for qi_sequence, data in qi_frequency.items():
                    if data[0] < k:
                        qi_frequency.pop(qi_sequence)

                # Start to read the table file from the start:
                self.table.seek(0)

                for i, row in enumerate(self.table):

                    table_row = self._get_values(row, list(self.attributes), i)

                    # Skip this row if it must be ignored:
                    if table_row is None:
                        continue

                    # Find sequence corresponding to this row index:
                    for qi_sequence in qi_frequency:
                        if i in qi_frequency[qi_sequence][1]:
                            line = self._set_values(table_row, qi_sequence, qi_names)
                            print(line, file=output, end="")
                            break

                break

        output.close()
