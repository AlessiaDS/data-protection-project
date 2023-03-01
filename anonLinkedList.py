# A linked list that receives the generalized qi-sequence with the
# corresponding combination of generalization
class Node:

    def __init__(self, qi_seq, combination):
        self.qi_seq = qi_seq
        self.child = None
        self.weight = sum(combination)


class LinkList:

    def __init__(self):
        self.root = None

    def add_node(self, node):

        root = self.find_root()
        current_node = root
        if root.weight > node.weight:
            node.children = root
        if root.weight < node.weight:
            if current_node.child is not None:
                current_node.child = node
            else:
                while node.weight > current_node.weight:
                    if node.weight < current_node.child:
                        temp_node = current_node.child
                        current_node.child = node
                        node.child = temp_node
                    current_node = current_node.child

    def find_root(self):
        current_node = self.node
        while current_node is not None:
            current_node = current_node.parent
        return current_node