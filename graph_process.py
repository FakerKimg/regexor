from fsm_to_graph import *
import networkx
from regexfsm.lego import *
import string

# process the graph

# generate SCCs
sccs = networkx.strongly_connected_component_subgraphs(g, copy=True)
sccs = sorted(sccs, key=len, reverse=True)

not_dag_edges = []

for scc in sccs:
    not_dag_edges = not_dag_edges + scc.edges()

dag_edges = [edge for edge in g.edges() if edge not in not_dag_edges]

# give SCC index to each node, usefull ?????
i = 0
for scc in sccs:
    scc_nodes = scc.nodes()
    for node in scc_nodes:
        g.node[node]["scc_index"] = i
    i = i + 1

# find boundary nodes in each SCC
for scc in sccs:
    scc.graph["inward_nodes"] = set()
    scc.graph["outward_nodes"] = set()

# add initial state and final states
initial_index = g.graph["initial"]
sccs[g.node[initial_index]["scc_index"]].graph["inward_nodes"].add(initial_index)

final_indexes = g.graph["finals"]
for final_index in final_indexes:
    sccs[g.node[final_index]["scc_index"]].graph["outward_nodes"].add(final_index)

# add other inward and outward nodes
for edge in dag_edges:
    for scc in sccs:
        if edge[0] in scc.nodes():
            scc.node[edge[0]].setdefault("outward_edges", [])
            scc.node[edge[0]]["outward_edges"].append(edge)
            scc.graph["outward_nodes"].add(edge[0])

        if edge[1] in scc.nodes():
            scc.node[edge[1]].setdefault("inward_edges", [])
            scc.node[edge[1]]["inward_edges"].append(edge)
            scc.graph["inward_nodes"].add(edge[1])

# it's easier to operate on list ???
for scc in sccs:
    scc.graph["inward_nodes"] = list(scc.graph["inward_nodes"])
    scc.graph["outward_nodes"] = list(scc.graph["outward_nodes"])


# algorithms for finding paths

def find_shortest_paths_pairs(scc):
    shortest_paths = []
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            shortest_paths.append(networkx.shortest_path(scc, inward_node, outward_node))

    return shortest_paths




def extract_edge_input(edge):
    #else_chars = [chr(i) for i in range(0, 256) if chr(i) not in g.graph["alphabet"]] # assume the alphabet is all ascii, anything_else represents all ascii except those in alphabet of regex(fsm)
    else_chars = [c for c in string.printable if chr(i) not in g.graph["alphabet"]]
    _inputs = g.edge[edge[0]][edge[1]]["_inputs"]

    pattern_str = "["
    for _input in _inputs:
        if _input==anything_else:
            for c in else_chars:
                if c in ['-', '[', ']', '\\', '^']:
                    pattern_str  = pattern_str + "\\" + c
                    continue
                pattern_str = pattern_str + c
        elif _input in ['-', '[', ']', '\\', '^']:
            pattern_str  = pattern_str + "\\" + _input
        else:
            pattern_str = pattern_str + _input
    pattern_str = pattern_str + "]"

    return pattern_str






for scc in sccs:
    #scc.graph["final_patterns"] = []
    #scc.graph["not_final_patters"] = []

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
            scc.node[path[0]]["patterns"][path[-1]] = parse(pattern_str).reduce()


#dag = networkx.condensation(g, sccs)



def iterate_scc(scc, inward_node, _pattern, output_patterns=[]):
    _patterns = scc.node[inward_node]["patterns"]
    for eindex, scc_pattern in _patterns.iteritems():
        if not scc_pattern:
            out_patterns = iterate_dag_edges(scc, eindex, _pattern, output_patterns)
            continue

        new_pattern = (_pattern + scc_pattern).reduce()
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


""" old code

for scc in sccs:
    scc.graph["replaceable_graphs"] = []

    shortest_paths = find_shortest_paths_pairs(scc)

    for shortest_path in shortest_paths:
        rg = networkx.DiGraph()
        if len(shortest_path)==1:
            rg.add_node(shortest_path[0])

        for i in range(0, len(shortest_path)-1):
            rg.add_edge(shortest_path[i], shortest_path[i+1])

        scc.graph["replaceable_graphs"].append(rg)





# create simplified graphs
def create_simplified_graphs(g, sccs, scc_index, simplified_graph, simplified_graphs):
    scc = sccs[scc_index]
    for replaceable_graph in scc.graph["replaceable_graphs"]:
        sg = networkx.DiGraph(simplified_graph)
        if len(replaceable_graph.edges())==0:
            sg.add_nodes_from(replaceable_graph.nodes())

        for edge in replaceable_graph.edges():
            sg.add_edge(edge[0], edge[1])
            sg.edge[edge[0]][edge[1]]["_inputs"] = list(g.edge[edge[0]][edge[1]]["_inputs"])

        if scc_index == len(sccs)-1:
            simplified_graphs.append(sg)
        else:
            create_simplified_graphs(g, sccs, scc_index+1, sg, simplified_graphs)

    return

def add_dag_edges(g, simplified_graphs, dag_edges):
    for simplified_graph in simplified_graphs:
        for edge in dag_edges:
            assert(edge not in simplified_graph.edges()) # ?????
            if edge[0] not in simplified_graph.nodes() or edge[1] not in simplified_graph.nodes():
                continue

            simplified_graph.add_edge(edge[0], edge[1])
            simplified_graph.edge[edge[0]][edge[1]]["_inputs"]=list(g.edge[edge[0]][edge[1]]["_inputs"])
    return

def check_fsm_usability(simplified_graphs):
    new_simplified_graphs = []
    for simplified_graph in simplified_graphs:
        for final in simplified_graph.graph["finals"]:
            try:
                networkx.shortest_path(simplified_graph, simplified_graph.graph["initial"], final)
                new_simplified_graphs.append(simplified_graph)
                break
            except Exception as e: # no nodes or no path between nodes
                print e

    return new_simplified_graphs

simplified_graphs = []
sg = networkx.DiGraph(alphabet=g.graph["alphabet"], initial=g.graph["initial"], finals=g.graph["finals"])

create_simplified_graphs(g, sccs, 0, sg, simplified_graphs)
add_dag_edges(g, simplified_graphs, dag_edges)
simplified_graphs = check_fsm_usability(simplified_graphs)

"""



