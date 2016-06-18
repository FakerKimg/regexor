from fsm_to_graph import *
import networkx
from regexfsm.lego import *

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


# algoritms for finding paths through dag
condenseg = networkx.condensation(g, sccs)

for edge in dag_edges:
    sscc_index = g.node[edge[0]]["scc_index"]
    escc_index = g.node[edge[1]]["scc_index"]

    condenseg.edge[sscc_index][escc_index].setdefault("condensed_edges", [])
    condenseg.edge[sscc_index][escc_index]["condensed_edges"].append(edge)

# add fake finals (or I should do it on the original graph ??????????????????)
final_sccs = set()
for final in g.graph["finals"]:
    final_sccs.add(g.node[final]["scc_index"])
final_sccs = list(final_sccs)

for final_scc in final_sccs:
    condenseg.add_edge(final_scc, str(final_scc)+"_final")
    condenseg.edge[final_scc][str(final_scc)+"_final"]["_inputs"] = [None]

def simply_bfs(condenseg):
    initial_scc = g.node[g.graph["initial"]]["scc_index"]
    condense_tree = networkx.bfs_tree(condenseg, initial_scc)
    dag_paths = []
    for final_scc in final_sccs:
        path = networkx.shortest_path(condense_tree, initial_scc, final_scc)
        dag_paths.append(path)

    condenseg.graph["dag_paths"] = dag_paths
    return dag_paths

def find_continue_path(condenseg, condense_tree, leaf):
    if "continue_path" in condense_tree.node[leaf].keys():
        return
    next_node = condenseg.edge[leaf].keys()[0] # choose any one edge ??????
    continue_edge = condenseg.edge[leaf][next_node]
    
    sub_tree = networkx.bfs_tree(condense_tree, next_node)
    sub_leaves = [node for node in sub_tree.nodes() if sub_tree.out_degree(node)==0 and sub_tree.in_degree(node)==1]
    for sub_leaf in sub_leaves:
        if "_final" in sub_leaf:
            condense_tree.node[leaf]["continue_path"] = [leaf] + networkx.shortest_path(condense_tree, next_node, sub_leaf)
            return
        else:
            find_continue_path(condenseg, condense_tree, sub_leaf)

    condense_tree.node[leaf]["continue_path"] = [leaf] + networkx.shortest_path(condense_tree, next_node, sub_leaves[0])  + condense_tree.node[sub_leaves[0]]["continue_path"][1:] # choose any one sub leaf, sub_leaf is the last of sub_leaves ??????????

    return

def all_bfs_branch(condenseg):
    initial_scc = g.node[g.graph["initial"]]["scc_index"]
    condense_tree = networkx.bfs_tree(condenseg, initial_scc)
    dag_paths = []
    leaves = [node for node in condense_tree.nodes() if condense_tree.out_degree(node)==0 and condense_tree.in_degree(node)==1]
    for leaf in leaves:
        if "_final" in leaf:
            path = networkx.shortest_path(condense_tree, initial_scc, leaf)
        else:
            find_continue_path(condenseg, condense_tree, leaf)
            path = networkx.shortest_path(condense_tree, initial_scc, leaf)
            path = path + condense_tree[leaf]["continue_path"][1:]
        dag_paths.append(path)

    condenseg.graph["dag_paths"] = dag_paths
    return dag_paths

def all_dag_covers(confenseg):
    dag_paths = all_bfs_branch(condenseg)

    initial_scc = g.node[g.graph["initial"]]["scc_index"]
    condense_tree = networkx.bfs_tree(condenseg, initial_scc)
    rest_edges = [edge for edge in confenseg.edges() if edge not in condense_tree.edges()]
    for rest_edge in rest_edges:
        path = networkx.shortest_path(condense_tree, initial_scc, rest_edge[0])
        _node = rest_edge[1]
        while True:
            if condense_tree.out_degree(_node)==0 and condense_tree.in_degree(_node)==1:
                if "_final" in _node:
                    path = path.append(_node)
                else:
                    path = path + condense_tree.node[_node]["continue_path"]
                break
            else:
                path.append(_node)
                _node = condense_tree.edge[_node].keys()[0]

        dag_paths.append(path)

    condenseg.graph["dag_paths"] = dag_paths
    return dag_paths


def gather_condense_dag_edges(condenseg):
    dag_edges = set()
    for dag_path in condenseg.graph["dag_paths"]:
        for i in range(0, len(dag_path)-1):
            dag_edges.add((dag_path[i], dag_path[i+1]))

    condenseg.graph["dag_edges"] = list(dag_edges)
    return

# algorithms for finding paths (in SCC????)

shortest_paths = []
for scc in sccs:
    shortest_paths.append(networkx.shortest_path(scc))

def find_shortest_paths(scc, scc_index):
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [shortest_paths[scc_index][inward_node][outward_node]]
    return


def complete_saleman_path(scc, scc_index, p, rns, outward_node):
    _path = list(p)
    rest_nodes = rns

    # for now, simply complete the nodes in order......
    while True:
        if len(rest_nodes)==0:
            break
        node = rest_nodes[0]
        _path = _path + shortest_paths[scc_index][_path[-1]][node]
        rest_nodes = [node for node in scc.nodes() if (node not in _path) and (node!=outward_node)]

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
            _path = complete_saleman_path(scc, scc_index, _path, rest_nodes, outward_node)
            _path = _path + shortest_paths[scc_index][_path[-1]][outward_node]

            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [_path]

    return

def radiation_and_pack_paths(scc, scc_index):
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            innodes = [node for node in scc.nodes() if node!=inward_node and node!=outward_node]
            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [[inward_node, outward_node]] if len(innodes)==0 and inward_node!=outward_node else [[inward_node]]
            for innode in innodes:
                scc.node[inward_node]["scc_paths"][outward_node].append(shortest_paths[scc_index][inward_node][innode][:-1] + shortest_paths[scc_index][innode][outward_node])

            repeated_paths = []
            _len = len(scc.node[inward_node]["scc_paths"][outward_node])
            for i in range(0, _len):
                for j in range(i+1, _len):
                    if scc.node[inward_node]["scc_paths"][outward_node][i]==scc.node[inward_node]["scc_paths"][outward_node][j]:
                        repeated_paths.append(i)
                        break

            scc.node[inward_node]["scc_paths"][outward_node] = [scc.node[inward_node]["scc_paths"][outward_node][i] for i in range(0, _len) if i not in repeated_paths]

    return



simply_bfs(condenseg)
#all_bfs_branch(condenseg)
#all_dag_covers(condenseg)
gather_condense_dag_edges(condenseg)

i = 0
for scc in sccs:
    find_shortest_paths(sccs[i], i)
    #find_fake_saleman_paths(sccs[i], i)
    #radiation_and_pack_paths(sccs[i], i)

    i = i + 1

