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

    # works with pointer to tuple
    def addEdge(self, c1, c2):
        return self.add_edge(c1, c2)

    # attrs = {0: {"is_marked": False, "comb": "s:0,a:0,z:0"}}
    def addVertex(self, node, attr):
        #self.nodes[node]['isMarked'] = False
        return self.add_node(node, attr=attr)

    # Variant from original hasVertex, returns True or False
    def hasVertex(self, a):
        return self.has_node(a)

    def getRoots(self):
        tmp = []
        for n, d in self.in_degree():
            if d == 0:
                tmp.append(n)
        return tmp

    # criteria to add edge
    def add_linked_edge(self, qi_name):

        chars = "({})' "

        attributes = self.getVerticesAttributes()
        print(attributes)
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
        print(combs)

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

# passo i qi cosi controllo meno
#cercare metodo per trovare direttamente nodi

if __name__ == "__main__":
    qi_names = ["sex", "age", "zipcode"]
    G = MyDiGraph()
    G.add_node("sex:0;age:0;zipcode:0")
    G.nodes["sex:0;age:0;zipcode:0"]['is_marked'] = False
    G.add_node("sex:1;age:0;zipcode:0")
    G.nodes["sex:1;age:0;zipcode:0"]['is_marked'] = False
    G.add_node("sex:0;age:1;zipcode:0")
    G.nodes["sex:0;age:1;zipcode:0"]['is_marked'] = False
    G.add_node("sex:0;age:2;zipcode:0")
    G.nodes["sex:0;age:2;zipcode:0"]['is_marked'] = False
    # G.nodes[0]['comb'] = "s:0,a:0,z:0"
    # print(G.nodes.data())
    vertexes = G.getVerticesAttributes()
    print(G.getVertices())
    G.add_linked_edge(qi_names)
    print(G.getEdges())
