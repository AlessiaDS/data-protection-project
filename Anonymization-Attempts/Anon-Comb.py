
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
    qi_frequency = dict() # K = Tuple ("a1","b2","c1") aka QI_seq, V = (int rep, set {"row_index_1","row_index_n"})

    # List of dictionaries where every iteration of the modified tables will be saved
    qi_frequency_candidates = list()

    # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
    # sets containing the corresponding domain elements:
    domains = dict() # K = 0,1,2,... "Index" of QI, V = set {QI_val 1, QI_val 2, ...}
    for i, attribute in enumerate(qi_names):
        domains[i] = set()

    # Dictionary whose keys are the indices in the QI attribute names list, and whose values are
    # the current levels of generalization, from 0 (not generalized):
    gen_levels = dict()
    for i, attribute in enumerate(qi_names):
        gen_levels[i] = 0

    # Initialize qi_frequency
    for i, row in enumerate(self.table):
        # i = index row
        # row value
        qi_sequence = self._get_values(row, qi_names, i) #list of values contained in qi_names at row 'i'

        # Skip if this row must be ignored:
        if qi_sequence is not None:
            qi_sequence = tuple(qi_sequence) #list -> tuple ("val_a","val_b","val_c")

        if qi_sequence in qi_frequency: #if qi_val_combination in qi_frequency Key
            occurrences = qi_frequency[qi_sequence][0] + 1 # add occurence of qi_sequence
            rows_set = qi_frequency[qi_sequence][1].union([i]) # add index
            qi_frequency[qi_sequence] = (occurrences, rows_set) # update value
        else:
            # Initialize number of occurrences and set of row indices:
            qi_frequency[qi_sequence] = (1, set())
            qi_frequency[qi_sequence][1].add(i)

            # Update domain set for each attribute in this sequence:
            for j, value in enumerate(qi_sequence):
                domains[j].add(value) #j = "index" of a qi attribute

    # ---------------------------START PART 1 - Generalization---------------------------
    # create QI_Combination list to follow
    combinations = combination(qi_names,dghs) # return a list of tuple combinations (?)

    for data in combinations: # data = (gen_lv of atr0, gen_lv of atr1, etc...), es. (0,0,1)
        # Generalize each value for that attribute and update the attribute set in the
        # domains dictionary:
        for i in range(len(data)):
            if data[i] != gen_levels[i]:
                domains[i] = set()
        # ---domains[attribute_idx] = set()
        # Look up table for the generalized values, to avoid searching in hierarchies:
        generalizations = dict()
        # generalized value to apply for the needed lables
        generalized_value = dict()

        # Note: using the list of keys since the dictionary is changed in size at runtime
        # and it can't be used as an iterator:
        for j, qi_sequence in enumerate(list(qi_frequency)):

            # Get the generalized value:
            for i in range(len(data)):
                if data[i] != gen_levels[i]:
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

            # Update domain set with this attribute value:
            domains[i].add(qi_sequence[i])

        # Update current level of generalization:
        for i in range(len(data)):
            gen_levels[i] = data[i]

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
            if i in qi_frequency[qi_sequence][1]: # if index row is in the set of indexes
                line = self._set_values(table_row, qi_sequence, qi_names)
                print(line, file=output, end="")
                break

    output.close()

# ---------------------------END PART2 - Write on output file---------------------------

# These methods rely on the existence of another method (dghs.length()) to retrive the total height of a Tree
# Currently said method doesn't exist, so it should be implemented in the tree.py file
def combination(qi_names, dghs):
    comb = list() # List of Tuples containing (gen_lv_of_qi1, gen_lv_ok_qi2, ...)
    rec_length = len(qi_names) - 1

    recursiveComb(rec_length, qi_names, dghs, comb)

    return comb

# Here "base" is going to be used to build the combinations of the generalization levels
def recursiveComb(rec_length,qi_names,dghs,comb,base=None):
    if rec_length != 0:
        #for as many times as how deep is the related Hierarchy Tree
        for i in range(dghs.length(qi_names[rec_length])):
            recursiveComb(rec_length - 1, qi_names, dghs, comb, base+(i,))
    else:
        for i in range(dghs.length(qi_names[rec_length])):
            comb.append(base + (i,))
