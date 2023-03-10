import networkx as nx

class MyDiGraph(nx.DiGraph):

    def getVertices(self):
        return self.nodes

    def getEdges(self):
        return self.edges

    # No need for "copy", can be done with a simple: new_graph = nx.DiGraph(graph_to_copy)

    def numEdges(self):
        return self.number_of_edges()

    def numVertices(self):
        return self.number_of_nodes()

    # works with pointer to tuple
    def addEdge(self, a, b):
        return self.add_edge(a, b)

    def addVertex(self, a):
        return self.add_node(a)

    # works with pointer to tuple
    def removeEdge(self, a, b):
        return self.remove_edge(a, b)

    def removeVertex(self, a):
        return self.remove_node(a)

    # previous format: i -> child (+ data related to it)
    # current: need to add the display of the data related to the children
    def printOut(self):
        for i in self.nodes:
            print("Current Node: ", i)
            if self.in_degree(i) != 0:
                print("Parent: ", list(self.in_edges(i))[0][0], "\nChildren: ", end="")
            else:
                print("Parent: Is root\nChildren: ", end="")

            if self.out_degree(i) != 0:
                for a, b in self.out_edges(i):
                    print(b, end=" ")
                print("\n")
            else:
                print("None\n")

    '''
    Not needed because the vertex (node) itself isn't an object itself
    def getVertex(graph, a):

    def hasVertex(graph, a):

    def hasVertex2(graph, a):
    '''

    #Variant from original hasVertex, returns True or False
    def hasVertex(self, a):
        return self.has_node(a)

    def getRoots(self):
        tmp = []
        for n, d in self.in_degree():
            if d == 0:
                tmp.append(n)
        return tmp


