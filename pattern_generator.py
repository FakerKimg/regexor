#from graph_process import *
from condense_graph_process import *
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



def iterate_scc(condense_path, condense_path_index, inward_node, _path, output_paths, use_condense_path):
    scc = sccs[condense_path[condense_path_index]]
    assert(inward_node in scc.nodes())
    for eindex, scc_paths in scc.node[inward_node]["scc_paths"].iteritems():
        for scc_path in scc_paths:
            new_path = _path + scc_path
            if condense_path_index==len(condense_path)-1:
                if eindex in g.graph["finals"]:
                    output_paths.append(new_path)
            else:
                iterate_dag_edges(condense_path, condense_path_index, eindex, new_path, output_paths, use_condense_path)

    return

def iterate_dag_edges(condense_path, condense_path_index, outward_node, _path, output_paths, use_condense_path):
    condense_edge = (condense_path[condense_path_index], condense_path[condense_path_index+1])
    _dag_edges = condenseg.edge[condense_edge[0]][condense_edge[1]]["condensed_edges"]
    if len(_dag_edges)==0: # condense_path_index+1 is fake final
        output_paths.append(_path)

    for _dag_edge in _dag_edges:
        if outward_node!=_dag_edge[0] and use_condense_path:
            continue
        iterate_scc(condense_path, condense_path_index+1, _dag_edge[1], _path, output_paths, use_condense_path)

    return


def iterate_condense_paths(condenseg, use_condense_path=True):
    output_paths = []
    inward_node = g.graph["initial"]
    if not use_condense_path:
        iterate_scc(condense_path, 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object
    else:
        for condense_path in condenseg.graph["condense_paths"]:
            iterate_scc(condense_path, 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object

    return output_paths



initial = g.graph["initial"]
use_condense_path = True if len(dag_edges)*4 > len(g.edges()) else False # this condition ??????????
output_paths = iterate_condense_paths(condenseg, use_condense_path)
print "output_paths complete"


def iterate_output(wf, output_path, pindex, output_str="", inputs_num=1):
    if pindex==len(output_path)-1:
        wf.write(output_str)
        wf.write("\n")
        return

    possible_inputs = extract_edge_inputs((output_path[0], output_path[1]))
    num = 0
    while True:
        if num==inputs_num or len(possible_inputs)==0:
            break
        _input = possible_inputs[random.randint(0, len(possible_inputs)-1)]
        iterate_output(wf, output_path, pindex+1, output_str+_input)
        possible_inputs.remove(_input)
        num = num + 1

    return

def generate_pattern(filename):
    with open(filename, "w") as wf:
        for output_path in output_paths:
            #wf.write(str(output_path) + "\n")
            iterate_output(wf, output_path, 0, "")

        wf.close()

    return

