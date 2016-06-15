from regexfsm.fsm import *
from FAdo.fa import *
import string
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls

def greenfsm_to_FDFA(gfsm):
    dfa = DFA()

    # no need to add sigma, because the DFA would add sigma automatically when adding transition
    # use string.printable as alphabet
    #dfa.addSigma(string.printable[:-6])
    else_chars = [c for c in string.printable[:-6] if c not in gfsm.__dict__["alphabet"]]
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

    symbol_mapping = {}
    nrepeat = 1 # num repeat
    ien = 0 # index of english letters
    # add transitions
    for sindex, transition in gfsm.__dict__["map"].iteritems():
        temp_mapping = {}
        for _input, eindex in transition.iteritems():
            if eindex not in temp_mapping.keys():
                temp_mapping[eindex] = {
                    "symbol": string.letters[ien] * nrepeat ,
                    "_inputs": []
                }
                ien = ien + 1
                if ien==len(string.letters):
                    ien = 0
                    nrepeat = nrepeat + 1

            if isinstance(_input, anything_else_cls):
                for else_input in else_chars:
                    temp_mapping[eindex]["_inputs"].append(else_input)
                dfa.addTransition(states_mapping[sindex], temp_mapping[eindex]["symbol"], states_mapping[eindex])
            else:
                temp_mapping[eindex]["_inputs"].append(_input)
                dfa.addTransition(states_mapping[sindex], temp_mapping[eindex]["symbol"], states_mapping[eindex])

        for eindex, _map in temp_mapping.iteritems():
            symbol_mapping[_map["symbol"]] = _map["_inputs"]

    return (dfa, symbol_mapping)


def iterate_Fregex(Fregex, symbol_mapping):
    if isinstance(Fregex, atom):
        char_set = ""
        for cc in symbol_mapping[Fregex.val]:
            if cc in "[^\-]": # ???????????????
                char_set = char_set + "\\" + cc
            else:
                char_set = char_set + cc
        return "[" + char_set + "]"
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
        elif not arg1:
            return arg2
        elif not arg2:
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

def FFA_to_regex(fa, symbol_mapping):
    Fregex = fa.regexpSE()
    print "FSM -> Fregex, complete"
    restr = iterate_Fregex(Fregex, symbol_mapping)

    return restr

