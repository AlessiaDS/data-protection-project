
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

    # List of Tuples that will save the state of the table at specific generalization levels
    # Will be needed to reset the Table to a desirable state qhile generalizing by following combinations
    qi_frequency_states = list() # Es. [0] = 000; [1] = xx0; [2] = x00

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

    # ---------------------------START PART 1 - Generalization---------------------------
    # save the state 000 on qi_frequency_states[0]
    qi_frequency_states[0] = dict(qi_frequency)

    qi_heights = list()

    for i in qi_names:
        qi_heights.append(range(dghs[i].get_tree_height()))

    # create QI_Combination list to follow
    combinations = combination(qi_heights) #combination(qi_names,dghs) # return a list of tuple combinations (?)

    print(combinations)

    for data in combinations: # data = (gen_lv of atr0, gen_lv of atr1, etc...), es. (0,0,1)
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
            if i in qi_frequency[qi_sequence][1]: # if index row is in the set of indexes
                line = self._set_values(table_row, qi_sequence, qi_names)
                print(line, file=output, end="")
                break

    output.close()

# ---------------------------END PART2 - Write on output file---------------------------

# New combination
import itertools

def combination (heights: list()):
    #dgh = [[0, 1], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3]]
    #comb = list(itertools.product(*heights))
    return list(itertools.product(*heights))

# Sample domain generalization hierarchy
dgh = [['0', '1'], ['0', '1', '2', '3', '4','5'], ['0', '1', '2', '3']]

# Get all possible combinations
combinations = list(itertools.product(*dgh))

# Print the combinations
print(combinations)

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
            recursiveComb(rec_length - 1, qi_names, dghs, comb, (i,) + base)
    else:
        for i in range(dghs.length(qi_names[rec_length])):
            comb.append(base + (i,))

# states_list len = qi_names len
# states_list = reset 1-2-3-...
# might need to handle old_vars (dict) and new_vars (list of tuples) differences
# not only reset the state but change lvs to corresponding resetted state
def resetState (old_vars, new_vars, current_state, states_list):
    if old_vars[0] != 0 and new_vars[0] == 0:
        return recResetState(1, old_vars, new_vars, current_state, states_list)
    else:
        return  (-1,)

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

    for i in range(1, current_qi + 1):
        states = states + (i,)
    return states