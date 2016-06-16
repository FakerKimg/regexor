from regexfsm.lego import parse
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls
import json
import io
import sys
import os

mapping = {
    "tel": "",
    "search": "[^'\x22]+",
    "url": "[A-Za-z][A-Za-z0-9+\-.]*:(?://(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9A-Fa-f]{1,4}:){6}|::(?:[0-9A-Fa-f]{1,4}:){5}|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,1}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}|(?:(?:[0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}|(?:(?:[0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:|(?:(?:[0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})?::)(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})?::)|[Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*)(?::[0-9]*)?(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*|/(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?|((?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?)(?:\?(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?(#(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?",
    "email": "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*",
    "date": "((((19|[2-9]\d)\d{2})-(0[13578]|1[02])-(0[1-9]|[12]\d|3[01]))|(((19|[2-9]\d)\d{2})-(0[13456789]|1[012])-(0[1-9]|[12]\d|30))|(((19|[2-9]\d)\d{2})-02-(0[1-9]|1\d|2[0-8]))|(((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00))-02-29))",
    "time": "([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9](.[0-9]{1,3})?)?",
    "number": "[\-+]?[0-9]*(.[0-9]*)?[eE][\-+]?[0-9]*",
    "range": "[\-+]?[0-9]*(.[0-9]*)?[eE][\-+]?[0-9]*",
    "color": "#[0-9a-fA-F]{6}",
}

with open("valid.fsms", "w") as fsmf:
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



"""
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

print fsm_dict
"""
