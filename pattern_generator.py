from graph_process import *



else_chars = [c for c in string.printable[:-6] if chr(i) not in g.graph["alphabet"]]

def extract_edge_input(edge):
    _inputs = g.edge[edge[0]][edge[1]]["_inputs"]

    possible_inputs = ""
    for _input in _inputs:
        if _input==anything_else:
            for c in else_chars:
                possible_inputs = possible_inputs + c
            continue
        possible_inputs = possible_inputs + _input

    return possible_inputs



def iterate_scc(scc, inward_node, _path, _paths=[]):
    new_paths = _paths
    for eindex, scc_paths in scc.node[inward_node]["scc_paths"].iteritems():
        for scc_path in scc_paths:
            new_path = _path + scc_path
            if eindex in g.graph["finals"]:
                new_paths.append(new_path)
            new_paths = iterate_dag_edges(scc, eindex, new_path, new_paths)

    return new_paths

def iterate_dag_edges(scc, outward_node, _path, _paths):
    outward_edges = scc.node[outward_node]["outward_edges"]
    new_paths = _paths
    for edge in outward_edges:
        new_scc = sccs[g.node[edge[1]]["scc_index"]]
        new_paths = iterate_scc(new_scc, edge[1], _path, new_paths)

    return new_paths



initial = g.graph["initial"]
output_paths = iterate_scc(sccs[g.node[initial]["scc_index"]], initial, [])



