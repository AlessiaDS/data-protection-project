import itertools
import csv
import sys
from io import StringIO
from dgh import CsvDGH
from tree import Tree

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

def combination (heights: list()):
    return list(itertools.product(heights))

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

    dgh_paths = dict()

    table_path = r"C:\Users\giamp\PycharmProjects\pythonProject\DP-Project2\tables\db_100.csv"

    qis = ("age", "sex", "zip_code")

    gen_paths = list()
    gen_paths.append(r"C:\Users\giamp\PycharmProjects\pythonProject\DP-Project2\tables\age_generalization.csv")
    gen_paths.append(r"C:\Users\giamp\PycharmProjects\pythonProject\DP-Project2\tables\sex_generalization.csv")
    gen_paths.append(r"C:\Users\giamp\PycharmProjects\pythonProject\DP-Project2\tables\zip_code_generalization.csv")

    for i, qi_name in enumerate(qis):
        dgh_paths[qi_name] = gen_paths[i]
    table = CsvTable(table_path, dgh_paths)

    # ---------------Start Testing Area------------------

    qi_heights = list()

    CsvDGH.getTreeHeight(table.dghs[qis[0]])

    #print(table.dghs[qis[0]].hierarchies['0-50'].root.children['0-20'].children['0-10'].children['1'].children)

    for i in qis:
        tmp = range(CsvDGH.getTreeHeight(table.dghs[i]))
        for n in tmp:
            
            print(n)
        qi_heights.append(tmp)

    print(qi_heights)

    # create QI_Combination list to follow
    combinations = combination(qi_heights)

    print(combinations)

    # anonymize
    # x is_k_anon
    # x suppress_under_k
    # x combination (test new version)
    # resetState
    # recResetState
    # getTreeHeight --------- obsolete
    # x get_tree_height --------- new, to check
    # x findMin return list L0 = GenComb, L1 = TableState
