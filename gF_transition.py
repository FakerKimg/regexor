from regexfsm.fsm import *
from FAdo.fa import *
import string
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls

def greenfsm_to_FDFA(gfsm):
    dfa = DFA()

    # use string.printable as alphabet
    dfa.addSigma(string.printable[:-6])
    else_chars = [c for c in string.printable[:-6] if c not in g.graph["alphabet"]]
    #else_chars = [c for c in string.printable if c not in gfsm.__dict__["alphabet"]]

    # add states
    states_mapping = {}
    for state in gfsm.__dict__["states"]:
        states_mapping[state] = dfa.addState(state)

    # set initial
    dfa.setInitial(states_mapping[gfsm.__dict__["initial"]])

    # set finals
    for final in list(gfsm.__dict__["finals"]):
        dfa.addFinal(states_mapping[final])

    # add transitions
    for sindex, transition in gfsm.__dict__["map"].iteritems():
        for _input, eindex in transition.iteritems():
            if isinstance(_input, anything_else_cls):
                for else_input in else_chars:
                    dfa.addTransition(states_mapping[sindex], else_input, states_mapping[eindex])
            else:
                dfa.addTransition(states_mapping[sindex], _input, states_mapping[eindex])

    return dfa


def iterate_Fregex(Fregex):
    if isinstance(Fregex, atom):
        return Fregex.val
    elif isinstance(Fregex, concat):
        arg1 = iterate_Fregex(Fregex.arg1)
        arg2 = iterate_Fregex(Fregex.arg2)
        if not arg1 and not arg2:
            return None
        elif not arg1:
            return arg2
        elif not arg2:
            return arg1
        return "(" + arg1 + arg2  + ")"
    elif isinstance(Fregex, disj):
        arg1 = iterate_Fregex(Fregex.arg1)
        arg2 = iterate_Fregex(Fregex.arg2)
        if not arg1 and not arg2:
            return None
        elif not arg1 or arg1=="":
            return arg2
        elif not arg2 or arg2=="":
            return arg1
        return "(" + arg1 + "|" + arg2  + ")"
    elif isinstance(Fregex, star):
        arg = iterate_Fregex(Fregex.arg)
        if not arg:
            return None
        return arg + "*"
    elif isinstance(Fregex, epsilon):
        return ""
    else: # emptyset ?????
        print Fregex
        pass

    return None

def FFA_to_regex(fa):
    Fregex = fa.regexpSE()
    print "FSM -> Fregex, complete"
    restr = iterate_Fregex(Fregex)

    return restr

