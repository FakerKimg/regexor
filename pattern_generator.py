from regexfsm.fsm import anything_else_cls
from graph_process import *
from condense_graph_process import *
from fsm_to_graph import *
import string
import random


def extract_edge_inputs(_graph, edge):

    _inputs = _graph.edge[edge[0]][edge[1]]["_inputs"]
    possible_inputs = []
    for _input in _inputs:
        if _input==anything_else:
            for else_char in else_chars:
                possible_inputs.append(else_char)
            continue
        possible_inputs.append(_input)

    return possible_inputs



def iterate_scc(_graph, sccs, condenseg, condense_path, condense_path_index, inward_node, _path, output_paths, use_condense_path):
    if not use_condense_path:
        scc = sccs[_graph.node[inward_node]["scc_index"]]
    else:
        scc = sccs[condense_path[condense_path_index]]
    assert(inward_node in scc.nodes())
    for eindex, scc_paths in scc.node[inward_node]["scc_paths"].iteritems():
        for scc_path in scc_paths:
            new_path = _path + scc_path
            assert(eindex==new_path[-1])
            if not use_condense_path:
                if eindex in _graph.graph["finals"]:
                    output_paths.append(new_path)
                iterate_dag_edges(_graph, sccs, condenseg, condense_path, condense_path_index, eindex, new_path, output_paths, use_condense_path)
                continue

            if condense_path_index==len(condense_path)-1:
                if eindex in _graph.graph["finals"]:
                    output_paths.append(new_path)
                else:
                    print "this path should end here????"
                    import pdb;pdb.set_trace()
            else:
                iterate_dag_edges(_graph, sccs, condenseg, condense_path, condense_path_index, eindex, new_path, output_paths, use_condense_path)

    return

def iterate_dag_edges(_graph, sccs, condenseg, condense_path, condense_path_index, outward_node, _path, output_paths, use_condense_path):
    if not use_condense_path:
        current_scc = sccs[_graph.node[outward_node]["scc_index"]]
        for outward_edge in current_scc.node[outward_node]["outward_edges"]:
            #next_scc = sccs[_graph.node[outward_edge[1]]["scc_index"]]
            #assert(outward_node in next_scc.nodes())
            iterate_scc(_graph, sccs, condenseg, condense_path, condense_path_index, outward_edge[1], _path, output_paths, use_condense_path)
        return

    condense_edge = (condense_path[condense_path_index], condense_path[condense_path_index+1])
    _dag_edges = condenseg.edge[condense_edge[0]][condense_edge[1]]["condensed_edges"]

    if len(_dag_edges)==0: # condense_path_index+1 is fake final
        assert("_final" in condense_edge[1])
        if _path[-1] in _graph.graph["finals"] and _path not in output_paths:
            output_paths.append(_path)

    for _dag_edge in _dag_edges:
        if outward_node!=_dag_edge[0]:
            continue
        iterate_scc(_graph, sccs, condenseg, condense_path, condense_path_index+1, _dag_edge[1], _path, output_paths, use_condense_path)

    return


def iterate_condense_paths(_graph, _sccs, _condenseg, use_condense_path=True):
    output_paths = []
    inward_node = _graph.graph["initial"]
    if not use_condense_path: # not covered ????
        iterate_scc(_graph, _sccs, _condenseg, _condenseg.graph["condense_paths"][0], 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object
    else:
        for condense_path in _condenseg.graph["condense_paths"]:
            iterate_scc(_graph, _sccs, _condenseg, condense_path, 0, inward_node, [], output_paths, use_condense_path) # i beleive in python's pass by object

    return output_paths


def fsm_graph_process(_g, _sccs, dag_edges, _condenseg, final_sccs, shortest_paths, scc_type="shortest", condense_type="simplybfs"):
    scc_process(_sccs, shortest_paths, scc_type)
    condense_process(_g, _condenseg, final_sccs, condense_type)

    #use_condense_path = True if len(dag_edges)*4 > len(_g.edges()) else False # this condition ??????????
    use_condense_path = True
    output_paths = iterate_condense_paths(_g, _sccs, _condenseg, use_condense_path)
    print "output_paths complete"

    return [_path for _path in output_paths if len(_path)>1]


def iterate_output(wf, _graph, output_path, pindex, output_str="", inputs_num=1):
    if pindex==len(output_path)-1:
        if output_str!="":
            wf.write(output_str)
            wf.write("\n")
        return

    else_chars = [c for c in string.printable[:-6] if c not in _graph.graph["alphabet"]]
    #else_chars = [c for c in string.printable if c not in _graph.graph["alphabet"]]


    if len(output_path)>100: # python iteration repeat times limititaion ????
        sss = ""
        for i in range(0, len(output_path)-1):
            #possible_inputs = extract_edge_inputs((output_path[pindex], output_path[pindex+1]))
            possible_inputs = list(_graph.edge[output_path[i]][output_path[i+1]]["_inputs"])
            if len(possible_inputs)==0:
                assert("dead_" in output_path[i])
                assert(output_path[i+1].startswith(output_path[i]))
                continue

            selected_input = random.sample(possible_inputs, 1)[0]
            if isinstance(selected_input, anything_else_cls):
                selected_input = random.sample(else_chars, 1)[0]

            sss = sss + selected_input
        wf.write(sss)
        wf.write("\n")
        return


    #possible_inputs = extract_edge_inputs((output_path[pindex], output_path[pindex+1]))
    possible_inputs = list(_graph.edge[output_path[pindex]][output_path[pindex+1]]["_inputs"])

    if len(possible_inputs)==0: # edge that dead_xx -> dead_xx_??_::
        assert("dead_" in output_path[pindex])
        assert(output_path[pindex+1].startswith(output_path[pindex]))
        iterate_output(wf, _graph, output_path, pindex+1, output_str, inputs_num)
        return

    selected_inputs = random.sample(possible_inputs, inputs_num)
    for selected_input in selected_inputs:
        if isinstance(selected_input, anything_else_cls):
            else_input = random.sample(else_chars, 1)[0]
            iterate_output(wf, _graph, output_path, pindex+1, output_str+else_input, inputs_num)
        else:
            iterate_output(wf, _graph, output_path, pindex+1, output_str+selected_input, inputs_num)

    return

def generate_patterns(_type, scc_type, condense_type, valid):
    dead_state_index = {
        "tel": 2,
        "url": 1,
        "email": 2,
        "date": 1,
        "time": 1,
        "number": 4,
        "range": 4,
        "color": 2,
    } # use dead_state_check.py to check


    valid_graph, invalid_graph = fsm_graph_transition(_type)
    _graph = valid_graph if valid else expand_invalid_graph(valid_graph, invalid_graph, dead_state_index[_type])
    sccs, dag_edges = basic_graph_process(_graph)
    condenseg, final_sccs = basic_condenseg_process(_graph, sccs, dag_edges)
    shortest_paths = create_shortest_path(sccs)
    output_paths = fsm_graph_process(_graph, sccs, dag_edges, condenseg, final_sccs, shortest_paths, scc_type, condense_type)

    return _graph, output_paths

def output_patterns(filename, _graph, _output_paths, num):
    with open("./test_patterns/" + filename, "w") as wf:
        _num = num
        while True:
            if _num<=0:
                break
            elif _num>=len(_output_paths):
                for output_path in _output_paths:
                    #wf.write(str(output_path) + "\n")
                    iterate_output(wf, _graph, output_path, 0, "")
            else:
                _temp_paths = random.sample(_output_paths, _num)
                for output_path in _temp_paths:
                    #wf.write(str(output_path) + "\n")
                    iterate_output(wf, _graph, output_path, 0, "")

            _num = _num - len(_output_paths)
        wf.close()

    return

