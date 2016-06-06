from regexfsm.lego import pattern
from regexfsm.fsm import anything_else
from regexfsm.fsm import anything_else_cls
import json
import io
import string
from FAdo.reex import *

sss = "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*"

#sss = "a*"

ppp = pattern.parse(sss)


# pattern in greenery, disjoint in FAdo
def parse_pattern(_pattern, sigma=string.printable):
    concs = list(_pattern.concs)
    if len(concs)==1:
        return parse_conc(concs[0], sigma)

    temp_regex = disj(parse_conc(concs[0], sigma), parse_conc(concs[1], sigma), sigma)
    for conc in concs[2:]:
        temp_regex = disj(temp_regex, parse_conc(conc, sigma), sigma)

    return temp_regex

# concation in greenery and FAdo
def parse_conc(_conc, sigma):
    mults = list(_conc.mults)
    if len(mults)==1:
        return parse_mult(mults[0], sigma)

    temp_regex = concat(parse_mult(mults[0], sigma), parse_mult(mults[1], sigma), sigma)
    for mult in mults[2:]:
        temp_regex = concat(temp_regex, parse_mult(mult, sigma), sigma)

    return temp_regex

# mult(etc. Keelen star) in greenery, use concat and disjoint in FAdo
def parse_mult(_mult, sigma):
    _min = _mult.multiplier.min.v
    _max = _mult.multiplier.max.v
    multiplicand = _mult.multiplicand

    if _min==0:
        temp_regex = epsilon()
    elif _min==1:
        temp_regex = parse_multiplicand(multiplicand, sigma)
    else:
        temp_regex = concat(parse_multiplicand(multiplicand, sigma), parse_multiplicand(multiplicand, sigma))
        for i in range(0, _min-2):
            temp_regex = concat(temp_regex, parse_multiplicand(multiplicand, sigma))

    if not _max: # max is infinity????
        temp_regex = concat( temp_regex, star(parse_multiplicand(multiplicand, sigma)) )
    else:
        for i in range(0, _max-_min):
            # tr = tr | concat(tr, multiplicand)
            temp_regex = disj(temp_regex, concat(temp_regex, parse_multiplicand(multiplicand, sigma)))

    return temp_regex


def parse_multiplicand(_multiplicand, sigma):
    if "charclass" in str(_multiplicand.__class__):
        chars = list(_multiplicand.chars)
        if _multiplicand.negated:
            chars = [c for c in sigma if c not in chars]

        temp_regex = atom(chars[0], sigma)
        for c in chars[1:]:
            temp_regex = disj(temp_regex, atom(c, sigma), sigma)
    elif "pattern" in str(_multiplicand.__class__):
        temp_regex = parse_pattern(_multiplicand, sigma)

    return temp_regex


temp_regex = parse_pattern(ppp, string.printable[:-6])


