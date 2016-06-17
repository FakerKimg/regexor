from regexfsm.fsm import fsm
from regexfsm.fsm import anything_else
import json
import networkx

f = open("valid.fsms", "r")
fsm_json = f.readline()
f.close()



fsm_dict = json.loads(fsm_json)
fsm_dict = fsm_dict["date"]

# copy alphabet
cpalphabet = [ s.encode("utf-8") for s in fsm_dict["alphabet"] ]
if "anything_else" in cpalphabet:
    cpalphabet.remove("anything_else")
    cpalphabet.append(anything_else)

# copy map
cpmap = {}
for sstate, edges in fsm_dict["map"].iteritems():
    sindex = int(sstate)
    cpmap[sindex] = {}
    for _input, eindex in edges.iteritems():
        if _input=="anything_else":
            cpmap[sindex][anything_else] = eindex
        else:
            cpmap[sindex][_input.encode("utf-8")] = eindex

valid_fsm = fsm(alphabet=set(cpalphabet), states=set(fsm_dict["states"]), initial=fsm_dict["initial"], finals=set(fsm_dict["finals"]), map=cpmap)
negative_fsm = valid_fsm.everythingbut()



g = networkx.DiGraph(initial=negative_fsm.initial, finals=list(negative_fsm.finals), alphabet=cpalphabet)
g.add_nodes_from(list(negative_fsm.states))

# use add_edges_from will be better ???
for sindex, edges in negative_fsm.map.iteritems():
    for _input, eindex in edges.iteritems():
        g.add_edge(sindex, eindex)
        g.edge[sindex][eindex].setdefault("_inputs", [])
        if _input not in g.edge[sindex][eindex]["_inputs"]:
            g.edge[sindex][eindex]["_inputs"].append(_input)

print "graph construction complete"

