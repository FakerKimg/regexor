from gF_transition import *
from fsm_to_graph import *



def dfa_generate():
    negative_dfa = greenfsm_to_FDFA(negative_fsm)
    ng = negative_dfa.works()


