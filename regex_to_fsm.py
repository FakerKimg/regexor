from regexfsm.lego import pattern
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls
import json
import io

sss = "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*"

#sss = "a*"

m = pattern.parse(sss).to_fsm().everythingbut()

m_dict = {}
for key, value in m.__dict__.iteritems():
    v = value
    if type(value) == set:
        v = list(v)
    m_dict[key] = v

"""
class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, anything_else_cls):
            return {"object": "anything_else"}

        return json.JSONEncoder.default(self, o)

print m_dict
m_json = MyEncoder().encode(m_dict)
"""


if anything_else in m_dict["alphabet"]:
    m_dict["alphabet"].remove(anything_else)
    m_dict["alphabet"].append("anything_else")

for snode, edges in m_dict["map"].iteritems():
    if anything_else not in edges.keys():
        continue
    edges["anything_else"] = edges[anything_else]
    del edges[anything_else]


m_json = json.dumps(m_dict)

f = open("email_valid_fsm", "w")
f.write(m_json)
f.close()


"""
with io.open("email_valid_fsm", "w", encoding='utf8') as json_file:
    json.dumps(m_dict, json_file, ensure_ascii=False)
"""

print "complete"

