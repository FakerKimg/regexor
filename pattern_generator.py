from graph_process import *




# algorithms for finding paths

def find_shortest_paths_pairs(scc):
    shortest_paths = []
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            shortest_paths.append(networkx.shortest_path(scc, inward_node, outward_node))

    return shortest_paths



#else_chars = [chr(i) for i in range(0, 256) if chr(i) not in g.graph["alphabet"]] # assume the alphabet is all ascii, anything_else represents all ascii except those in alphabet of regex(fsm)
else_chars = [c for c in string.printable if chr(i) not in g.graph["alphabet"]]

def extract_edge_input(edge):
    _inputs = g.edge[edge[0]][edge[1]]["_inputs"]

    pattern_str = "["
    for _input in _inputs:
        if _input==anything_else:
            for c in else_chars:
                if c in "-[]\\^":
                    pattern_str  = pattern_str + "\\" + c
                    continue
                pattern_str = pattern_str + c
        elif _input in "-[]\\^":
            pattern_str  = pattern_str + "\\" + _input
        else:
            pattern_str = pattern_str + _input
    pattern_str = pattern_str + "]"

    return pattern_str


for scc in sccs:
    paths = find_shortest_paths_pairs(scc)

    scc.graph["paths"] = paths
    for path in paths:
        pattern_str = ""
        for i in range(0, len(path)-1):
            pattern_str = pattern_str + extract_edge_input( (path[i], path[i+1]) )

        scc.node[path[0]].setdefault("patterns", {})

        if pattern_str=="":
            scc.node[path[0]]["patterns"][path[-1]] = None
        else:
            scc.node[path[0]]["patterns"][path[-1]] = parse(pattern_str)


def iterate_scc(scc, inward_node, _pattern, output_patterns=[]):
    _patterns = scc.node[inward_node]["patterns"]
    for eindex, scc_pattern in _patterns.iteritems():
        if scc_pattern == None:
            out_patterns = iterate_dag_edges(scc, eindex, _pattern, output_patterns)
            continue

        new_pattern = (_pattern + scc_pattern)
        output_patterns = iterate_dag_edges(scc, eindex, new_pattern, output_patterns)

        if eindex in g.graph["finals"]:
            output_patterns.append(new_pattern)

    return output_patterns


def iterate_dag_edges(scc, outward_node, _pattern, output_patterns=[]):
    outward_edges = scc.node[outward_node]["outward_edges"]
    for edge in outward_edges:
        new_scc = sccs[g.node[edge[1]]["scc_index"]]
        edge_input_str = extract_edge_input( (edge[0], edge[1]) )
        output_patterns = iterate_scc(new_scc, edge[1], _pattern + parse(edge_input_str), output_patterns)

    return output_patterns


initial = g.graph["initial"]
out_patterns = iterate_scc(sccs[g.node[initial]["scc_index"]], initial, pattern())




