from regexfsm.lego import *
from regexfsm.fsm import *
import networkx

else_chars = 

def copy_gnfa(fsm_graph):
    # copy the graph
    cg = networkx.DiGraph(alphabet=fsm_graph.graph["alphabet"], initial=fsm_graph.graph["initial"], finals=fsm_graph["finals"])
    for _edge in fsm_graph.edges():
        cg.add_edge(_edge[0], _edge[1])
        char_set = set()
        for _input in g.edge[_edge[0]][_edge[1]]["_inputs"]:
            if isinstance(_input, anything_else_cls):
                for else_c in else_chars:
                    char_set.add(else_c)
            char_set.add(_input)

        cg.edge[_edge[0]][_edge[1]]["pattern"] = charclass(char_set)

    cg.add_edge("start", cg.graph["initial"])
    cg.edge["start"][cg.graph["initial"]]["pattern"] = None

    for final in cg.graph["finals"]:
        cg.add_edge(final, "final")
        cg.edge[final]["final"]["pattern"] = None

    return cg

def self_Brzozowski_alg(gnfa):


