from fsm_to_graph import *

dead_state_index = {
    "tel": 2,
    "url": 1,
    "email": 2,
    "date": 1,
    "time": 1,
    "number": 4,
    "range": 4,
    "color": 2,
} # ??????



# check dead node
for input_type in dead_state_index.keys():
    print input_type
    validg, invalidg = fsm_graph_transition(input_type)

    dead_states = [node for node in invalidg.nodes() if invalidg.out_degree(node)==1 and node in invalidg.edge[node].keys()]
    assert(len(dead_states)==1)
    assert(dead_states[0]==dead_state_index[input_type])


    dead_node = dead_state_index[input_type]
    for invalid_edge in invalidg.edges():
        # check corresponding edges in valid graph
        valid_start = invalid_edge[0] if invalid_edge[0]<dead_node else invalid_edge[0]-1
        valid_end = invalid_edge[1] if invalid_edge[1]<dead_node else invalid_edge[1]-1
        valid_edge = (valid_start, valid_end)
        if invalid_edge[0]==dead_node or invalid_edge[1]==dead_node:
            continue

        if valid_edge in validg.edges():
            if set(validg.edge[valid_start][valid_end]["_inputs"])!=set(invalidg.edge[invalid_edge[0]][invalid_edge[1]]["_inputs"]):
                print "invalid edge: ", invalid_edge, ", valid edge: ", valid_edge, " ... wrong corresponding"
                import pdb;pdb.set_trace()

