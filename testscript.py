from graph_process import *
from gF_transition import *

dfa, _mmm = greenfsm_to_FDFA(negative_fsm)
rrr = FFA_to_regex(dfa, _mmm)

