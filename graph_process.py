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

# add inward and outward nodes
for edge in dag_edges:
    scc_index = g.node[edge[0]]["scc_index"]
    scc = sccs[scc_index]
    scc.node[edge[0]].setdefault("outward_edges", [])
    scc.node[edge[0]]["outward_edges"].append(edge)
    scc.graph["outward_nodes"].add(edge[0])

    scc_index = g.node[edge[1]]["scc_index"]
    scc = sccs[scc_index]
    scc.node[edge[1]].setdefault("inward_edges", [])
    scc.node[edge[1]]["inward_edges"].append(edge)
    scc.graph["inward_nodes"].add(edge[1])

# initial must be add to inward nodes, add final states if the final state node not outward node
initial_index = g.graph["initial"]
sccs[g.node[initial_index]["scc_index"]].graph["inward_nodes"].add(initial_index)
sccs[g.node[initial_index]["scc_index"]].node[initial_index].setdefault("inward_edges", [])

final_indexes = g.graph["finals"]
for final_index in final_indexes:
    scc_index = g.node[final_index]["scc_index"]
    scc = sccs[scc_index]
    scc.graph["outward_nodes"].add(final_index)
    scc.node[final_index].setdefault("outward_edges", [])


# it's easier to operate on list ???
for scc in sccs:
    scc.graph["inward_nodes"] = list(scc.graph["inward_nodes"])
    scc.graph["outward_nodes"] = list(scc.graph["outward_nodes"])


# algorithms for finding paths

shortest_paths = []
for scc in sccs:
    shortest_paths.append(networkx.shortest_path(scc))

def find_shortest_paths(scc, scc_index):
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = shortest_paths[scc_index][inward_node][outward_node]
    return


def complete_saleman_path(scc, scc_index, p, rns):
    _path = list(p)
    rest_nodes = rns

    # for now, simply complete the nodes in order......
    while True:
        if len(rns)==0:
            break
        node = rest_nodes[0]
        _path = _path + shortest_paths[scc_index][_path[-1]][node]
        rest_nodes = [node for node in scc.nodes() if (node not in _path) or (node!=outward_node)]

    #rest_nodes = [node for node in scc.nodes() if node not in _path]

    return _path


def find_fake_saleman_paths(scc, scc_index):
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            scc.node[inward_node].setdefault("scc_paths", {})
            _max = 0
            _eindex = inward_node
            for eindex, path in shortest_paths[scc_index][inward_node].iteritems():
                if eindex==outward_node:
                    continue
                _eindex = eindex if _max < len(path) else _eindex
                _max = len(path) if _max < len(path) else _max

            _path = shortest_paths[scc_index][inward_node][_eindex] if _eindex!=inward_node else [inward_node]
            rest_nodes = [node for node in scc.nodes() if (node not in _path) or (node!=outward_node)]
            _path = complete_saleman_path(scc, scc_index, _path, rest_nodes)
            _path = _path + shortest_paths[scc_index][_path[-1]][outward_node]

            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = _path

    return


i = 0
for scc in sccs:
    find_shortest_paths(scc, i)
    i = i + 1



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



