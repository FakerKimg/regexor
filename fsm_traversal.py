from regexfsm.fsm import *
import random
from regexfsm.fsm import anything_else_cls
from regexfsm.fsm import anything_else

# assume we get a graph represented a fsm, and a node represented the state where we are
def next_step(g, n, possible_stop):
    if n in g.graph["finals"]:
        num = random.randint(0, len(string.printable[:-6]))
        if num==len(string[:-6]):
            return ("", None)
    else:
        num = random.randint(0, len(string.printable[:-6])-1)

    _input = string.printable[num]
    _input = anything_else if _input in else_chars else _input

    for eindex, edge in g.edge[n].iteritems():
        if _input in edge["_inputs"]:
            break

    return (_input, eindex)


def output_generator(g):

