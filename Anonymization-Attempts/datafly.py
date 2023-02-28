import argparse
import csv
import sys
import itertools
from datetime import datetime
from io import StringIO
from dgh import CsvDGH


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

        # Start reading the table file (the one to anonymize) from the top:
        self.table.seek(0)

        # Dictionary whose keys are sequences of values for the Quasi Identifiers and whose values
        # are couples (n, s) where n is the number of occurrences of a sequence and s is a set
        # containing the indices of the rows in the original table file with those QI values:
        qi_frequency = dict()  # K = Tuple ("a1","b2","c1") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

        # List of Tuples that will save the state of the table at specific generalization levels
        # Will be needed to reset the Table to a desirable state while generalizing by following combinations
        qi_frequency_states = list()  # Es. [0] = 000; [1] = xx0; [2] = x00

        # List of dictionaries where every iteration of the modified tables will be saved
        qi_frequency_candidates = list()

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
        # save the state 000 on qi_frequency_states[0]
        qi_frequency_states[0] = dict(qi_frequency)

        qi_heights = list()

        for i in qi_names:
            qi_heights.append(range(self.dghs[i].get_tree_height()))

        # create QI_Combination list to follow
        combinations = combination(qi_heights)  # combination(qi_names,dghs) # return a list of tuple combinations (?)

        print(combinations)

        for data in combinations:  # data = (gen_lv of atr0, gen_lv of atr1, etc...), es. (0,0,1)
            # qi_frequency_states indexes that will be used to save the state of the table
            # at the end of the generalization
            saveState = resetState(gen_levels, data, qi_frequency, qi_frequency_states)
            # Look up table for the generalized values, to avoid searching in hierarchies:
            generalizations = dict()
            # Generalized value to apply for the needed lables
            generalized_value = dict()

            # Note: using the list of keys since the dictionary is changed in size at runtime
            # and it can't be used as an iterator:
            for j, qi_sequence in enumerate(list(qi_frequency)):

                # Get the generalized value:
                for i in range(len(data)):
                    # If QI is going back to genLv 0 then do nothing since it has already been "rolled back"
                    # with resetState
                    # If old and new level are the same then do nothing once again
                    if data[i] != 0 and data[i] != gen_levels[i]:
                        if qi_sequence[i] in generalizations:
                            # Find directly the generalized value in the look up table:
                            generalized_value[i] = generalizations[i]
                        else:
                            # Get the corresponding generalized value from the attribute DGH:
                            try:
                                generalized_value = self.dghs[qi_names[i]] \
                                    .generalize(
                                    qi_sequence[i],
                                    gen_levels[i])
                            except KeyError as error:
                                print(error)
                                output.close()
                                return

                            if generalized_value is None:
                                # Skip if it's a hierarchy root:
                                continue

                        # Add to the look up table:
                        generalizations[i] = generalized_value[i]
                        # probably instead of "attribute_idx" you should use "qi_sequence[attribute_idx]"

                # Tuple with generalized value:
                new_qi_sequence = list(qi_sequence)
                # change only the attributes that needed to be changed ->
                # the ones with a generalization level different from before
                for id, gen_val in generalized_value.items():
                    new_qi_sequence[id] = gen_val
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

            # Update current level of generalization:
            for i in range(len(data)):
                gen_levels[i] = data[i]

            # Saving the current state of the Table in the needed indexes
            if saveState != -1:
                for i in saveState:
                    qi_frequency_states[i] = dict(qi_frequency)

            # Add the current qi_frequency to the list of combination/table candidates
            qi_frequency_candidates.append(qi_frequency)

        # ---------------------------END PART1 - Generalization---------------------------

        #TODO:
        # Selection of the frequency set that is K-Anon and Minimal (from qi_frequency_candidates)
        # And save it in qi_frequency

        # ---------------------------START PART 2 - Write on output file---------------------------

        # Start suppression *ONLY AFTER* having all other tuples at k reps
        # Popped only from the dictionary and not from the table itself?
        # And write soon after
        self._debug("[DEBUG] Suppressing max k non k-anonymous tuples...")
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

def combination (heights):
    # es_heights = [[0, 1], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3]] -> [a,b,c]
    # returns ordered combinations: [[a0,b0,c0],[a0,b0,c1],[a0,b0,c2], ..., [a1, b5, c3]]
    return list(itertools.product(heights))

# old_vars and new_vars refer to the generalization levels
# current_state is the current state of the table that needs to be resetted
# states_list is a list of states saved to be applied depending on the reset needed
# states_list len = qi_names len
# states_list = reset 1-2-3-...
# might need to handle old_vars (dict) and new_vars (list of tuples) differences
# not only reset the state but change lvs to corresponding resetted state
def resetState (old_vars, new_vars, current_state, states_list):
    if old_vars[0] != 0 and new_vars[0] == 0:
        return recResetState(1, old_vars, new_vars, current_state, states_list)
    else:
        return  (-1,) #reset state not needed

def recResetState (current_qi, old_vars, new_vars, current_state, states_list):
    if current_qi < len(new_vars):
        if old_vars[current_qi] != 0:
            if new_vars[current_qi] == 0:
                return recResetState(current_qi+1, old_vars, new_vars, current_state, states_list)
            else:
                current_state = dict(states_list[current_qi])

        elif new_vars[current_qi+1] == 0:
            current_state = dict(states_list[0])
        else:
            current_state = dict(states_list[current_qi])

    elif current_qi == len(new_vars):
        if old_vars[current_qi] != 0:
            if new_vars[current_qi] != 0:
                current_state = dict(states_list[current_qi])
        else:
            current_state = dict(states_list[0])

    # will a touple that defines to which indexes save the state of the table after generalization
    # the index 0 gets skipped because is the origin state [000...0]
    # might need to define in another way, to check
    for i in range(1, current_qi + 1):
        states = states + (i,)
    return states

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
