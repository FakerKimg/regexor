import networkx

# algoritms for finding paths through dag

def dag_shortest_path(_graph, condenseg, final_sccs):
    initial_scc = _graph.node[_graph.graph["initial"]]["scc_index"]
    dag_paths = []
    for final_scc in final_sccs:
        path = networkx.shortest_path(condenseg, initial_scc, final_scc)
        dag_paths.append(path)

    condenseg.graph["condense_paths"] = dag_paths
    return dag_paths


def simply_bfs(_graph, condenseg, final_sccs):
    initial_scc = _graph.node[_graph.graph["initial"]]["scc_index"]
    condense_tree = networkx.bfs_tree(condenseg, initial_scc)
    dag_paths = []
    for final_scc in final_sccs:
        path = networkx.shortest_path(condense_tree, initial_scc, final_scc)
        dag_paths.append(path)

    condenseg.graph["condense_paths"] = dag_paths
    return dag_paths


def find_continue_path(condenseg, condense_tree, leaf):
    if "continue_path" in condense_tree.node[leaf].keys():
        return
    next_node = condenseg.edge[leaf].keys()[0] # choose any one edge ??????
    continue_edge = condenseg.edge[leaf][next_node]

    sub_tree = networkx.bfs_tree(condense_tree, next_node)
    sub_leaves = [node for node in sub_tree.nodes() if sub_tree.out_degree(node)==0 and sub_tree.in_degree(node)==1]
    for sub_leaf in sub_leaves:
        if "_final" in str(sub_leaf):
            condense_tree.node[leaf]["continue_path"] = [leaf] + networkx.shortest_path(condense_tree, next_node, sub_leaf)
            return
        else:
            find_continue_path(condenseg, condense_tree, sub_leaf)

    if len(sub_leaves)==0:
        find_continue_path(condenseg, condense_tree, next_node)
        condense_tree.node[leaf]["continue_path"] = [leaf] + condense_tree.node[next_node]["continue_path"] # choose any one sub leaf, sub_leaf is the last of sub_leaves ??????????
    else:
        condense_tree.node[leaf]["continue_path"] = [leaf] + networkx.shortest_path(condense_tree, next_node, sub_leaves[0]) + condense_tree.node[sub_leaves[0]]["continue_path"][1:] # choose any one sub leaf, sub_leaf is the last of sub_leaves ??????????

    return


def all_tree_branch(_graph, condenseg, final_sccs, tree_type, ct=None):
    initial_scc = _graph.node[_graph.graph["initial"]]["scc_index"]
    if not ct:
        if tree_type=="bfs":
            condense_tree = networkx.bfs_tree(condenseg, initial_scc)
        elif tree_type=="dfs":
            condense_tree = networkx.dfs_tree(condenseg, initial_scc)
    else:
        condense_tree = ct
    dag_paths = []
    leaves = [node for node in condense_tree.nodes() if condense_tree.out_degree(node)==0 and condense_tree.in_degree(node)==1]
    for leaf in leaves:
        if "_final" in str(leaf):
            path = networkx.shortest_path(condense_tree, initial_scc, leaf)
        else:
            find_continue_path(condenseg, condense_tree, leaf)
            path = networkx.shortest_path(condense_tree, initial_scc, leaf)
            path = path + condense_tree.node[leaf]["continue_path"][1:]
        dag_paths.append(path)

    condenseg.graph["condense_paths"] = dag_paths
    return dag_paths


def all_dag_covers(_graph, condenseg, final_sccs, tree_type):
    initial_scc = _graph.node[_graph.graph["initial"]]["scc_index"]
    if tree_type=="bfs":
        condense_tree = networkx.bfs_tree(condenseg, initial_scc)
    elif tree_type=="dfs":
        condense_tree = networkx.dfs_tree(condenseg, initial_scc)
    rest_edges = [edge for edge in condenseg.edges() if edge not in condense_tree.edges()]

    all_tree_branch(_graph, condenseg, final_sccs, tree_type, condense_tree)
    dag_paths = condenseg.graph["condense_paths"]
    for rest_edge in rest_edges:
        path = networkx.shortest_path(condense_tree, initial_scc, rest_edge[0])
        _node = rest_edge[1]
        while True:
            if condense_tree.out_degree(_node)==0 and condense_tree.in_degree(_node)==1:
                if "_final" in str(_node):
                    path.append(_node)
                else:
                    path = path + condense_tree.node[_node]["continue_path"]
                break
            else:
                path.append(_node)
                _node = condense_tree.edge[_node].keys()[0]

        dag_paths.append(path)

    condenseg.graph["condense_paths"] = dag_paths
    return dag_paths


def gather_condense_dag_edges(condenseg):
    dag_edges = set()
    for dag_path in condenseg.graph["condense_paths"]:
        for i in range(0, len(dag_path)-1):
            dag_edges.add((dag_path[i], dag_path[i+1]))

    condenseg.graph["condense_edges"] = list(dag_edges)
    return

def basic_condenseg_process(_graph, sccs, dag_edges):
    condenseg = networkx.condensation(_graph, sccs)

    for edge in dag_edges:
        sscc_index = _graph.node[edge[0]]["scc_index"]
        escc_index = _graph.node[edge[1]]["scc_index"]

        condenseg.edge[sscc_index][escc_index].setdefault("condensed_edges", [])
        condenseg.edge[sscc_index][escc_index]["condensed_edges"].append(edge)


    # add fake finals (or I should do it on the original graph ??????????????????)
    final_sccs = set()
    for final in _graph.graph["finals"]:
        final_sccs.add(_graph.node[final]["scc_index"])
    final_sccs = list(final_sccs)
    condenseg.graph["final_sccs"] = final_sccs

    for final_scc in final_sccs:
        condenseg.add_edge(final_scc, str(final_scc)+"_final")
        condenseg.edge[final_scc][str(final_scc)+"_final"]["condensed_edges"] = []

    return condenseg, final_sccs


def condense_process(_graph, _condenseg, final_sccs, _type="simplybfs"):
    if _type=="shortest":
        dag_shortest_path(_graph, _condenseg, final_sccs)
    elif _type=="simplybfs":
        all_tree_branch(_graph, _condenseg, final_sccs, "bfs")
    elif _type=="simplydfs":
        all_tree_branch(_graph, _condenseg, final_sccs, "dfs")
    elif _type=="allcoverbfs":
        all_dag_covers(_graph, _condenseg, final_sccs, "bfs")
    elif _type=="allcoverdfs":
        all_dag_covers(_graph, _condenseg, final_sccs, "dfs")
    #gather_condense_dag_edges(_condenseg)

    return

