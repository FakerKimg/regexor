from fsm_to_graph import *

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
    for node in scc.nodes():
        g.node[node]["scc_index"] = i
    i = i + 1

# find boundary nodes in each SCC
for scc in sccs:
    scc.graph.setdefault("inward_nodes", [])
    scc.graph.setdefault("outward_nodes", [])

# add initial state and final states
initial_index = g.graph["initial"]
sccs[g.node[initial_index]["scc_index"]].graph["inward_nodes"].append(initial_index)

final_indexes = g.graph["finals"]
for final_index in final_indexes:
    sccs[g.node[final_index]["scc_index"]].graph["outward_nodes"].append(final_index)


for edge in dag_edges:
    for scc in sccs:
        if edge[0] in scc.nodes():
            scc.node[edge[0]].setdefault("outward_edges", [])
            scc.node[edge[0]]["outward_edges"].append(edge)
            if edge[0] not in scc.graph["outward_nodes"]:
                scc.graph["outward_nodes"].append(edge[0])

        if edge[1] in scc.nodes():
            scc.node[edge[1]].setdefault("inward_edges", [])
            scc.node[edge[1]]["inward_edges"].append(edge)
            if edge[1] not in scc.graph["inward_nodes"]:
                scc.graph["inward_nodes"].append(edge[1])


# find paths

def find_shortest_paths_pairs(scc):
    shortest_paths = []
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            shortest_paths.append(networkx.shortest_path(scc, inward_node, outward_node))

    return shortest_paths


for scc in sccs:
    scc.graph["replaceable_graphs"] = []

    shortest_paths = find_shortest_paths_pairs(scc)

    """
    rg = networkx.DiGraph()
    for shortest_path in shortest_paths:
        for i in range(0, len(shortest_path)-1):
            rg.add_edge(shortest_path[i], shortest_path[i+1])

    scc.graph["replaceable_graphs"].append(rg)
    """

    for shortest_path in shortest_paths:
        rg = networkx.DiGraph()
        for i in range(0, len(shortest_path)-1):
            rg.add_edge(shortest_path[i], shortest_path[i+1])

        scc.graph["replaceable_graphs"].append(rg)


# create simplified graphs

def create_simplified_graphs(g, sccs, scc_index, simplified_graph, simplified_graphs):
    for replaceable_graph in sccs[scc_index].graph["replaceable_graphs"]:
        sg = networkx.DiGraph(simplified_graph)
        for edge in replaceable_graph.edges():
            sg.add_edge(edge[0], edge[1])
            sg.edge[edge[0]][edge[1]]["_inputs"] = list(g.edge[edge[0]][edge[1]]["_inputs"])

        if scc_index == len(sccs)-1:
            simplified_graphs.append(sg)
        else:
            create_simplified_graphs(g, sccs, scc_index+1, sg, simplified_graphs)

simplified_graphs = []
sg = networkx.DiGraph(alphabet=g.graph["alphabet"], initial=g.graph["initial"], finals=g.graph["finals"])
for edge in dag_edges:
    sg.add_edge(edge[0], edge[1])
    sg.edge[edge[0]][edge[1]]["_inputs"] = list(g.edge[edge[0]][edge[1]]["_inputs"])

create_simplified_graphs(g, sccs, 0, sg, simplified_graphs)

