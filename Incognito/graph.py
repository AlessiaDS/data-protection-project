import itertools

import networkx as nx
import parsing


class MyDiGraph(nx.DiGraph):

    def getVertex(self, comb):
        return self.nodes[comb]

    def getVertices(self):
        return self.nodes

    def getVerticesAttributes(self):
        return self.nodes.data()

    def getEdges(self):
        return self.edges
    
    def getData(self, a):
        return self.nodes[a]["data"]

    # works with pointer to tuple
    def addEdge(self, c1, c2):
        return self.add_edge(c1, c2)

    def addVertex(self, node):
        self.add_node(node, is_marked=False)
        return self #return not needed
    
    def isMarked(self, a):
        return self.nodes[a]["marked"]
    
    def setMark(self, a):
        self.nodes[a]["marked"] = True

    def setData(self, a, data):
        self.nodes[a]["data"] = data
        
    def isRoot(self,a):
        return self.in_degree(a) == 0

    # Variant from original hasVertex, returns True or False
    def hasVertex(self, a):
        return self.has_node(a)

    def getRoots(self):
        tmp = []
        for n, d in self.in_degree():
            if d == 0:
                tmp.append(n)
        return tmp

    # previous format: i -> child (+ data related to it)
    # current: need to add the display of the data related to the children
    def printOut(self):
        for i in self.nodes:
            print("Node: ", i)
            print("Attributes: ")
            for j in self.nodes[i]:
                print("-",j,": ", self.nodes[i][j])

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
    
    def add_vertices(self, qi_height, qi_names):

        count = range(len(qi_names))
        listofcomb = list(itertools.product(*qi_height))
        print(listofcomb)
        dizionario = {}

        for combi in listofcomb:
            for index in count:
                key = qi_names[index]
                value = combi[index]
                dizionario[key] = value
                if index == (len(qi_names) - 1):
                    self.addVertex(parsing.reparse_attr(dizionario))
        return

    # criteria to add edge
    def add_linked_edge(self, qi_name):

        chars = "({})' "

        attributes = self.getVerticesAttributes()
        #print(attributes)
        list(attributes)
        attributes_s = []

        for e in attributes:
            st = str(e)
            st_mod = st.translate(str.maketrans('', '', chars))
            atrs = st_mod.split(",")
            attributes_s.append(str(atrs[0]))

        combs = {}

        for s in attributes_s:
            comb = parsing.parse_attr(s)
            combs[s] = comb
        #print(combs)

        vertices = self.getVertices()

        temp_combs = combs.copy()
        for q in qi_name:
            for c in combs:
                if combs[c].get(q) is not None:
                    temp = combs[c].get(q)
                    temp_combs[c][q] = int(temp) + 1

                combination2add = parsing.reparse_attr(temp_combs[c])
                combs[c][q] = int(temp)

                for v in vertices:
                    if v == combination2add:
                        for w in vertices:
                            if w == c:
                                self.add_edge(w, v)
        return


if __name__ == "__main__":
    qi_height = [[0, 1, 2]]
    qi_names = ["sex"]
    G = MyDiGraph()
    G.add_vertices(qi_height, qi_names)
    print(G.nodes)
    print(G)
    G.add_linked_edge(qi_names)
    print(G.getEdges())
    print(G)
