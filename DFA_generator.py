from gF_transition import *
from fsm_to_graph import *
import random




def dfa_generate(num):
    negative_dfa = greenfsm_to_FDFA(negative_fsm)
    ng = negative_dfa.words()

    outputs = []
    for i in range(0, num):
        value = random.getrandbits(48)
        while True:
            if value==0:
                break
            ng.next()
            value = value - 1

        print "one output"
        outputs.append(ng.next())

    return outputs


