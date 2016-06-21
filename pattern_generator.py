from regexfsm.fsm import anything_else_cls
from graph_process import *
from condense_graph_process import *
from fsm_to_graph import *
import string
import random

#else_chars = [c for c in string.printable[:-6] if c not in g.graph["alphabet"]]
#else_chars = [c for c in string.printable if c not in g.graph["alphabet"]]

def extract_edge_inputs(_graph, edge):
    else_chars = [c for c in string.printable[:-6] if c not in _graph.graph["alphabet"]]
    #else_chars = [c for c in string.printable if c not in _graph.graph["alphabet"]]

    _inputs = _graph.edge[edge[0]][edge[1]]["_inputs"]
    possible_inputs = []
    for _input in _inputs:
        if _input==anything_else:
            for c in else_chars:
                possible_inputs.append(c)
            continue
        possible_inputs.append(_input)

    return possible_inputs



def iterate_scc(_graph, sccs, condenseg, condense_path, condense_path_index, inward_node, _path, output_paths, use_condense_path):
    scc = sccs[condense_path[condense_path_index]]
    assert(inward_node in scc.nodes())
    for eindex, scc_paths in scc.node[inward_node]["scc_paths"].iteritems():
        for scc_path in scc_paths:
            new_path = _path + scc_path
            if condense_path_index==len(condense_path)-1:
                if eindex in _graph.graph["finals"]:
                    output_paths.append(new_path)
            else:
                iterate_dag_edges(_graph, sccs, condenseg, condense_path, condense_path_index, eindex, new_path, output_paths, use_condense_path)

    return

def iterate_dag_edges(_graph, sccs, condenseg, condense_path, condense_path_index, outward_node, _path, output_paths, use_condense_path):
    condense_edge = (condense_path[condense_path_index], condense_path[condense_path_index+1])
    _dag_edges = condenseg.edge[condense_edge[0]][condense_edge[1]]["condensed_edges"]

    if len(_dag_edges)==0: # condense_path_index+1 is fake final
        if _path[-1] in _graph.graph["finals"]:
            output_paths.append(_path)

    for _dag_edge in _dag_edges:
        if outward_node!=_dag_edge[0] and use_condense_path:
            continue
        iterate_scc(_graph, sccs, condenseg, condense_path, condense_path_index+1, _dag_edge[1], _path, output_paths, use_condense_path)

    return


def iterate_condense_paths(_graph, sccs, condenseg, use_condense_path=True):
    output_paths = []
    inward_node = _graph.graph["initial"]
    if not use_condense_path:
        iterate_scc(sccs, condenseg, condense_path, 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object
    else:
        for condense_path in condenseg.graph["condense_paths"]:
            iterate_scc(_graph, sccs, condenseg, condense_path, 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object

    return output_paths


def fsm_graph_process(_g, _sccs, dag_edges, _condenseg, final_sccs, shortest_paths, scc_type="shortest", condense_type="simplybfs"):
    scc_process(_sccs, shortest_paths, scc_type)
    condense_process(_g, _condenseg, final_sccs, condense_type)

    initial = _g.graph["initial"]
    use_condense_path = True if len(dag_edges)*4 > len(_g.edges()) else False # this condition ??????????
    output_paths = iterate_condense_paths(_g, _sccs, _condenseg, use_condense_path)
    print "output_paths complete"

    return output_paths


def iterate_output(wf, _graph, output_path, pindex, output_str="", inputs_num=1):
    if pindex==len(output_path)-1:
        wf.write(output_str)
        wf.write("\n")
        return

    else_chars = [c for c in string.printable[:-6] if c not in _graph.graph["alphabet"]]
    #else_chars = [c for c in string.printable if c not in _graph.graph["alphabet"]]

    #possible_inputs = extract_edge_inputs((output_path[pindex], output_path[pindex+1]))
    possible_inputs = list(_graph.edge[output_path[pindex]][output_path[pindex+1]]["_inputs"])
    num = 0
    while True:
        if num==inputs_num or len(possible_inputs)==0:
            break
        _input = possible_inputs[random.randint(0, len(possible_inputs)-1)]
        if isinstance(_input, anything_else_cls):
            else_input = else_chars[random.randint(0, len(else_chars)-1)]
            iterate_output(wf, _graph, output_path, pindex+1, output_str+else_input, inputs_num)
        else:
            iterate_output(wf, _graph, output_path, pindex+1, output_str+_input, inputs_num)
        possible_inputs.remove(_input)
        num = num + 1

    return

def generate_patterns(_type, scc_type, condense_type):
    valid_graph, _graph = fsm_graph_transition(_type)
    sccs, dag_edges = basic_graph_process(_graph)
    condenseg, final_sccs = basic_condenseg_process(_graph, sccs, dag_edges)
    shortest_paths = create_shortest_path(sccs)

    return _graph, fsm_graph_process(_graph, sccs, dag_edges, condenseg, final_sccs, shortest_paths, scc_type, condense_type)

def output_patterns(filename, _graph, _output_paths, times=1):
    with open(filename, "w") as wf:
        for i in range(0, times):
            for output_path in _output_paths:
                #wf.write(str(output_path) + "\n")
                iterate_output(wf, _graph, output_path, 0, "")

        wf.close()

    return

