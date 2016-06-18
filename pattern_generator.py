from graph_process import *
import string
import random

else_chars = [c for c in string.printable[:-6] if c not in g.graph["alphabet"]]
#else_chars = [c for c in string.printable if c not in g.graph["alphabet"]]

def extract_edge_inputs(edge):
    _inputs = g.edge[edge[0]][edge[1]]["_inputs"]

    possible_inputs = []
    for _input in _inputs:
        if _input==anything_else:
            for c in else_chars:
                possible_inputs.append(c)
            continue
        possible_inputs.append(_input)

    return possible_inputs



def iterate_scc(scc, inward_node, _path, _paths=[], use_condense_path=False):
    new_paths = _paths
    for eindex, scc_paths in scc.node[inward_node]["scc_paths"].iteritems():
        for scc_path in scc_paths:
            new_path = _path + scc_path
            if eindex in g.graph["finals"]:
                new_paths.append(new_path)
            new_paths = iterate_dag_edges(scc, eindex, new_path, new_paths, use_condense_path)

    return new_paths

def iterate_dag_edges(scc, outward_node, _path, _paths, use_condense_path=False):
    outward_edges = scc.node[outward_node]["outward_edges"]
    new_paths = _paths
    for edge in outward_edges:
        if use_condense_path:
            if (g.node[outward_node]["scc_index"], g.node[edge[1]]["scc_index"]) not in condenseg.graph["dag_edges"]:
                continue

        new_scc = sccs[g.node[edge[1]]["scc_index"]]
        new_paths = iterate_scc(new_scc, edge[1], _path, new_paths, use_condense_path)

    return new_paths



initial = g.graph["initial"]
use_condense_path = True if len(dag_edges)*4 > len(g.edges()) else False # this condition ??????????
output_paths = iterate_scc(sccs[g.node[initial]["scc_index"]], initial, [], use_condense_path)



def iterate_output(wf, output_path, pindex, output_str="", inputs_num=1):
    if pindex==len(output_path)-1:
        wf.write(output_str)
        wf.write("\n")
        return

    possible_inputs = extract_edge_inputs((output_path[0], output_path[1]))
    num = 0
    while True:
        if num==inputs_num or len(possible_inputs):
            break
        _input = possible_inputs[random.randint(0, len(possible_inputs)-1)]
        iterate_output(wf, output_path, pindex+1, output_str+_input)
        possible_inputs.remove(_input)
        num = num + 1

    return


"""
with open("email.shortest.pattern", "w") as wf:
    for output_path in output_paths:
        wf.write(str(output_path) + "\n")
        #iterate_output(wf, output_path, 0, "")

    wf.close()
"""

