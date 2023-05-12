import itertools
import parsing
import networkx as nx

class MyDiGraph(nx.DiGraph):

    def getVertex(self, a):
        return self.nodes[a]

    def getVertices(self):
        return self.nodes

    def getVerticesAttributes(self):
        return self.nodes.data()

    def getEdges(self):
        return self.edges

    def getData(self, a):
        return self.nodes[a]["data"]

    #No need for Graph "copy", can be done with a simple: new_graph = nx.DiGraph(graph_to_copy)

    def numEdges(self):
        return self.number_of_edges()

    def numVertices(self):
        return self.number_of_nodes()

    #works with pointer to tuple (data self adds "marked" which is set to 0)
    #Removed "return" because not needed
    def addEdge(self, a, b):
        self.add_edge(a, b)

    #Removed "return" because not needed
    def addVertex(self, a):
        self.add_node(a)
        #-------------------modified
        self.nodes[a]["marked"] = False

    #---------------------added
    #The gestion could be moved to "MyData"
    def isMarked(self, a):
        return self.nodes[a]["marked"]

    #---------------------added
    #The gestion could be moved to "MyData"
    #Removed "return" because not needed
    def setMark(self, a):
        self.nodes[a]["marked"] = True

    # TODO: To add
    def setData(self, a, data):
        self.nodes[a]["data"] = data

    #---------------------added
    def isRoot(self,a):
        return self.in_degree(a) == 0

    #def getDirectGeneralization returns a graph containing the Vertices that are directly connected to a
    #---------------------added
    def getDirectGeneralizations(self,a,graph):
        if graph.out_degree(a) != 0:
            for a,b in graph.out_edges(a):
                if not b in graph:
                    graph.addVertex(b)
        return graph

    #TODO: def toString prints the data content of a given node, depends on format of "data"

    def getIncidentEdges(self, a):
        return self.out_edges(a)

    def getNumOfIncidentEdges(self, a):
        return self.out_degree(a)

    #TODO: def getData return item saved in data, depends on format of "data"

    # works with pointer to tuple
    def removeEdge(self, a, b):
        return self.remove_edge(a, b)

    def removeVertex(self, a):
        return self.remove_node(a)

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

    #just changed name
    def hasVertex2(self, a):
        return self.has_node(a)

    def getRoots(self):
        tmp = []
        for n, d in self.in_degree():
            if d == 0:
                tmp.append(n)
        return tmp

    def add_vertices(self, qi_height, qi_names):

        #print("qi_height content: ",qi_height,"\nqi_names content: ",qi_names)

        count = range(len(qi_names))
        listofcomb = list(itertools.product(*qi_height))
        dizionario = {}

        for combi in listofcomb:
            for index in count:
                key = qi_names[index]
                value = combi[index]
                dizionario[key] = value
                if index == (len(qi_names) - 1):
                    self.addVertex(parsing.reparse_attr(dizionario))

        return

    def mono_add_linked_edge(self,qi_name):
        if not self.has_node(qi_name[0]+":"+str(0)):
            return -1
        count = 1
        precedent = qi_name[0]+":"+str(0)
        while True:
            current = qi_name[0]+":"+str(count)
            if self.has_node(current):
                self.add_edge(precedent,current)
                #print(current,"exists")
            else:
                #print(current,"doesn't")
                break
            precedent=current
            count+=1

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
        #print("combs: ",combs)

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


    #TODO: setData and getData in the list of things to understand how to handle

if __name__ == "__main__":
    qi_height = [[0,1,2]]
    qi_names = ["age"]
    G = MyDiGraph()
    G.add_vertices(qi_height, qi_names)
    G.mono_add_linked_edge(qi_names)
    #G.printOut()
    #print("Added Vertices: ",G.nodes)
    #print(G)
    #G.add_linked_edge(qi_names)
    #G.printOut()
    #print("Added Edges: ",G.getEdges())
    #print(G)
    qi_height = [[0, 1]]
    qi_names = ["sex"]
    G.add_vertices(qi_height, qi_names)
    G.mono_add_linked_edge(qi_names)
    #G.add_linked_edge(qi_names)
    G.printOut()
