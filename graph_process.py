import networkx
from regexfsm.lego import *

# process the graph

def basic_graph_process(_graph):
    # generate SCCs
    sccs = networkx.strongly_connected_component_subgraphs(_graph, copy=True)
    sccs = sorted(sccs, key=len, reverse=True)

    not_dag_edges = []

    for scc in sccs:
        not_dag_edges = not_dag_edges + scc.edges()

    dag_edges = [edge for edge in _graph.edges() if edge not in not_dag_edges]

    # give SCC index to each node, usefull ?????
    i = 0
    for scc in sccs:
        scc_nodes = scc.nodes()
        for node in scc_nodes:
            _graph.node[node]["scc_index"] = i
        i = i + 1

    # find boundary nodes in each SCC
    for scc in sccs:
        scc.graph["inward_nodes"] = set()
        scc.graph["outward_nodes"] = set()

    # add inward and outward nodes
    for edge in dag_edges:
        scc_index = _graph.node[edge[0]]["scc_index"]
        scc = sccs[scc_index]
        scc.node[edge[0]].setdefault("outward_edges", [])
        scc.node[edge[0]]["outward_edges"].append(edge)
        scc.graph["outward_nodes"].add(edge[0])

        scc_index = _graph.node[edge[1]]["scc_index"]
        scc = sccs[scc_index]
        scc.node[edge[1]].setdefault("inward_edges", [])
        scc.node[edge[1]]["inward_edges"].append(edge)
        scc.graph["inward_nodes"].add(edge[1])

    # initial must be add to inward nodes, add final states if the final state node not outward node
    initial_index = _graph.graph["initial"]
    sccs[_graph.node[initial_index]["scc_index"]].graph["inward_nodes"].add(initial_index)
    sccs[_graph.node[initial_index]["scc_index"]].node[initial_index].setdefault("inward_edges", [])

    final_indexes = _graph.graph["finals"]
    for final_index in final_indexes:
        scc_index = _graph.node[final_index]["scc_index"]
        scc = sccs[scc_index]
        scc.graph["outward_nodes"].add(final_index)
        scc.node[final_index].setdefault("outward_edges", [])


    # it's easier to operate on list ???
    for scc in sccs:
        scc.graph["inward_nodes"] = list(scc.graph["inward_nodes"])
        scc.graph["outward_nodes"] = list(scc.graph["outward_nodes"])

    return (sccs, dag_edges)

# algorithms for finding paths (in SCC????)

def create_shortest_path(sccs):
    shortest_paths = []
    for scc in sccs:
        shortest_paths.append(networkx.shortest_path(scc))

    return shortest_paths

def find_shortest_paths(scc, scc_index, shortest_paths):
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [shortest_paths[scc_index][inward_node][outward_node]]
    return


def complete_saleman_path(scc, scc_index, p, rns, outward_node, shortest_paths):
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


def find_fake_saleman_paths(scc, scc_index, shortest_paths):
    if len(scc.nodes())==1: # is it the only special situation ??????
        only_node = scc.nodes()[0]
        scc.node[only_node]["scc_paths"] = {}
        scc.node[only_node]["scc_paths"][only_node] = [[only_node]]
        return
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
            _path = complete_saleman_path(scc, scc_index, _path, rest_nodes, outward_node, shortest_paths)
            _path = _path + shortest_paths[scc_index][_path[-1]][outward_node]

            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [_path]

    return

def radiation_and_pack_paths(scc, scc_index, shortest_paths):
    if len(scc.nodes())==1: # is it the only special situation ??????
        only_node = scc.nodes()[0]
        scc.node[only_node]["scc_paths"] = {}
        scc.node[only_node]["scc_paths"][only_node] = [[only_node]]
        return
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


def scc_process(_sccs, shortest_paths, _type="shortest"):
    for i in range(0, len(_sccs)):
        if _type=="shortest":
            find_shortest_paths(_sccs[i], i, shortest_paths)
        elif _type=="fakesaleman":
            find_fake_saleman_paths(_sccs[i], i, shortest_paths)
        elif _type=="radiation":
            radiation_and_pack_paths(_sccs[i], i, shortest_paths)

    return

