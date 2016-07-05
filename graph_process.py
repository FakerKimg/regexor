import networkx
from regexfsm.lego import *

# process the graph

def basic_graph_process(_graph):
    # generate SCCs
    sccs = networkx.strongly_connected_component_subgraphs(_graph, copy=True)
    sccs = sorted(sccs, key=len, reverse=True)
    _graph.graph["sccs"] = sccs

    not_dag_edges = []

    for scc in sccs:
        not_dag_edges = not_dag_edges + scc.edges()

    dag_edges = [edge for edge in _graph.edges() if edge not in not_dag_edges]

    # give SCC index to each node, usefull ?????
    for i in range(0, len(sccs)):
        for node in sccs[i].nodes():
            _graph.node[node]["scc_index"] = i

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

    # initial must be add to inward nodes, add final states as outward nodes
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


def complete_saleman_path(scc, scc_index, p, inward_node, outward_node, shortest_paths):
    _path = list(p)

    # for now, simply complete the nodes in order......
    while True:
        rest_nodes = [node for node in scc.nodes() if (node not in _path) and (node!=outward_node) and (node!=inward_node)]
        if len(rest_nodes)==0:
            break
        node = rest_nodes[0]
        _path = _path[:-1] + shortest_paths[scc_index][_path[-1]][node]

    return _path


def find_fake_saleman_paths(scc, scc_index, shortest_paths):
    if len(scc.nodes())==1: # is it the only special situation ??????
        only_node = scc.nodes()[0]
        scc.node[only_node]["scc_paths"] = {}
        scc.node[only_node]["scc_paths"][only_node] = [[only_node]]
        return
    for inward_node in scc.graph["inward_nodes"]:
        for outward_node in scc.graph["outward_nodes"]:
            _path = []
            _start = inward_node
            while True:
                rest_nodes = [node for node in scc.nodes() if (node not in _path) and (node!=outward_node) and (node!=_start)]
                rest_nodes_set = set(rest_nodes)
                if len(rest_nodes)==0:
                    break

                minus_min = 0
                _max_discover = 0
                _eindex = _start
                for rest_node in rest_nodes:
                    _shortest_path = shortest_paths[scc_index][_start][rest_node]
                    if _max_discover<len(rest_nodes_set.intersection(set(_shortest_path))):
                        _eindex = rest_node
                        _max_discover = len(rest_nodes_set.intersection(set(_shortest_path)))
                    elif _max_discover==len(rest_nodes_set.intersection(set(_shortest_path))) and minus_min<-len(_shortest_path):
                        _eindex = rest_node
                        minus_min = -len(_shortest_path)

                _path = _path[:-1] + shortest_paths[scc_index][_start][_eindex]
                _start = _path[-1]

            _path = _path[:-1] + shortest_paths[scc_index][_start][outward_node]
            scc.node[inward_node].setdefault("scc_paths", {})
            scc.node[inward_node]["scc_paths"][outward_node] = [_path]

    return

def radiation_and_pack_paths(scc, scc_index, shortest_paths):
    if len(scc.nodes())==1: # is it the only special situation ??????
        only_node = scc.nodes()[0]
        scc.node[only_node]["scc_paths"] = {}
        scc.node[only_node]["scc_paths"][only_node] = [[only_node]]
        return

    rest_nodes = [node for node in scc.nodes() if node not in scc.graph["outward_nodes"] and node not in scc.graph["inward_nodes"]]
    for inward_node in scc.graph["inward_nodes"]:
        scc.node[inward_node].setdefault("scc_paths", {})
        for outward_node in scc.graph["outward_nodes"]:
            scc.node[inward_node]["scc_paths"].setdefault(outward_node, [])
            scc.node[inward_node]["scc_paths"][outward_node].append(shortest_paths[scc_index][inward_node][outward_node])

            for rest_node in rest_nodes:
                scc.node[inward_node]["scc_paths"][outward_node].append(shortest_paths[scc_index][inward_node][rest_node][:-1] + shortest_paths[scc_index][rest_node][outward_node])

            # should we check this ?????
            repeated_indexes = []
            for i in range(0, len(scc.node[inward_node]["scc_paths"][outward_node])):
                if scc.node[inward_node]["scc_paths"][outward_node][i] in scc.node[inward_node]["scc_paths"][outward_node][:i]:
                    repeated_indexes.append(i)

            scc.node[inward_node]["scc_paths"][outward_node] = [scc.node[inward_node]["scc_paths"][outward_node][i] for i in range(0, len(scc.node[inward_node]["scc_paths"][outward_node])) if i not in repeated_indexes]

    return


def scc_process(_sccs, shortest_paths, _type="shortest"):
    for i in range(0, len(_sccs)):
        if _type=="shortest":
            find_shortest_paths(_sccs[i], i, shortest_paths)
        elif _type=="all-vertices-covered":
            find_fake_saleman_paths(_sccs[i], i, shortest_paths)
        elif _type=="tripartie":
            radiation_and_pack_paths(_sccs[i], i, shortest_paths)

    return



def expand_invalid_graph(validg, invalidg, dead_state):
    g = networkx.DiGraph()
    g.graph["dead_state"] = dead_state
    g.graph["initial"] = invalidg.graph["initial"]
    g.graph["alphabet"] = invalidg.graph["alphabet"]

    finals_set = set([final for final in invalidg.graph["finals"] if final!=dead_state])

    # find direct path from each node in validg to finals
    validg_direct_paths = {}
    for node in validg.nodes():
        for final in validg.graph["finals"]:
            try:
                direct_path = networkx.shortest_path(validg, node, final)
                validg_direct_paths[node] = direct_path
                break
            except:
                pass
        assert(node in validg_direct_paths.keys())

    # copy edges and nodes from invalidg
    not_dead_edges = [edge for edge in invalidg.edges() if edge[1]!=dead_state]
    dead_edges = [edge for edge in invalidg.edges() if edge[1]==dead_state and edge[0]!=dead_state]

    for edge in not_dead_edges:
        g.add_edge(edge[0], edge[1], invalidg.edge[edge[0]][edge[1]])

    # process the edge to dead state
    for dead_edge in dead_edges:
        g.add_edge(dead_edge[0], "dead_"+str(dead_edge[0]), invalidg.edge[dead_edge[0]][dead_edge[1]])
        finals_set.add("dead_"+str(dead_edge[0]))

        enodes = invalidg.edge[dead_edge[0]].keys()
        for enode in enodes:
            if enode==dead_state:
                continue
            valid_node = enode if enode<dead_state else enode-1
            valid_path = validg_direct_paths[valid_node]
            prefix_str = "dead_"+str(dead_edge[0])+"_"+str(valid_node)+"_"
            g.add_edge("dead_"+str(dead_edge[0]), prefix_str+"0", {"_inputs": []})
            for i in range(0, len(valid_path)-1):
                g.add_edge(prefix_str+str(i), prefix_str+str(i+1), validg.edge[valid_path[i]][valid_path[i+1]])
            finals_set.add(prefix_str+str(len(valid_path)-1))

    g.graph["finals"] = list(finals_set)
    return g


