from graph_process import *
from regexfsm.lego import from_fsm

reduced_regexes = []

for simplified_graph in simplified_graphs:
    edge_mapping = {}
    real_alphabets = set()
    for sindex, edges in simplified_graph.edge.iteritems():
        edge_mapping[sindex] = {}
        for eindex, params in edges.iteritems():
            for _input in params["_inputs"]:
                edge_mapping[sindex][_input] = eindex
                real_alphabets.add(_input)

    real_finals = [final for final in simplified_graph.graph["finals"] if final in simplified_graph.nodes()]

    reduced_fsm = fsm(alphabet=real_alphabets, states=set(simplified_graph.nodes()), initial=simplified_graph.graph["initial"], finals=set(real_finals), map=edge_mapping)

    testm = reduced_fsm.reduce()
    reduced_regexes.append( str(from_fsm(testm)) )

    #reduced_regexes.append( str(from_fsm(reduced_fsm)) )


print sss
print reduced_regexes

