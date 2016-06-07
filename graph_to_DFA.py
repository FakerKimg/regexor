from graph_process import *
from regexfsm.lego import from_fsm
from FAdo.fa import *
import string
from regexfsm.fsm import anything_else

reduced_regexes = []
DFAs = []

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

    m = DFA()

    _abs = string.printable[:-6]
    m.setSigma(_abs)

    states_mapping = {}
    for state in list(reduced_fsm.states):
        r = m.addState(state)
        states_mapping[state] = r

    m.setInitial(states_mapping[reduced_fsm.initial])

    for final in list(reduced_fsm.finals):
        m.addFinal(states_mapping[final])

    for sindex, edges in reduced_fsm.map.iteritems():
        for _input, eindex in edges.iteritems():
            if _input==anything_else:
                _inputs = [ab for ab in _abs if ab not in reduced_fsm.alphabet]
                for rinput in _inputs:
                    m.addTransition(states_mapping[sindex], rinput, states_mapping[eindex])
            else:
               m.addTransition(states_mapping[sindex], _input, states_mapping[eindex])

    DFAs.append(m)

fado_regex = []
for dfa in DFAs:
    fado_regex.append(dfa.regexpSE())


