from regexfsm.lego import parse
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls
import json
import io
import sys
import os

mapping = {
    "tel": "",
    "search": "",
    "url": "",
    "email": "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*",
    "date": "",
    "time": "",
    "number": "",
    "range": "",
    "color": "",
}

with open("valid_fsms", "w") as fsmf:
    fsm_dict = {}
    for _type, _regex in mapping.iteritems():
        if _regex == "":
            continue

        try:
            _fsm = parse(_regex).to_fsm()
        except:
            print "error while transition to fsm"
            continue

        fsm_dict[_type] = {}
        for key, value in _fsm.__dict__.iteritems():
            v = value
            if type(value) == set:
                v = list(v)
            fsm_dict[_type][key] = v

        if anything_else in fsm_dict[_type]["alphabet"]:
            fsm_dict[_type]["alphabet"].remove(anything_else)
            fsm_dict[_type]["alphabet"].append("anything_else")

        for snode, edges in fsm_dict[_type]["map"].iteritems():
            if anything_else not in edges.keys():
                continue
            edges["anything_else"] = edges[anything_else]
            del edges[anything_else]

    fsm_json = json.dumps(fsm_dict)
    fsmf.write(fsm_json)
    fsmf.close()

