import re
from regexfsm.lego import *
import random
import string

valid_regexes = {
    "tel": "((\((0|\+886)2\)[0-9]{4}-[0-9]{4})|((0|\+886)9[0-9]{8}))",
    "url": "[A-Za-z][A-Za-z0-9+\-.]*:(?://(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9A-Fa-f]{1,4}:){6}|::(?:[0-9A-Fa-f]{1,4}:){5}|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,1}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}|(?:(?:[0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}|(?:(?:[0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:|(?:(?:[0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})?::)(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})?::)|[Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*)(?::[0-9]*)?(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*|/(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?|((?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?)(?:\?(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?(#(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?",
    "email": "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*",
    "date": "(([1-9]*[0-9]{4,}-(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|([1-9]*[0-9]{4,}-(0[13456789]|1[012])-(0[1-9]|[12][0-9]|30))|([1-9]*[0-9]{4,}-02-(0[1-9]|1[0-9]|2[0-8]))|([1-9]*([13579][26]|[02468][048])00-02-29)|([1-9]*[0-9]{2}([13579][26]|[2468][048]|04|08)-02-29))",
    "time": "([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9](\.[0-9]{1,3})?)?",
    "number": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
    "range": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
    "color": "#[0-9a-fA-F]{6}",
}



# turn regexfsm.lego into str acceptable by re
def regexfsm_to_str(_lego, for_grep=True):
    result_str = ""
    if isinstance(_lego, pattern):
        concs_list = list(_lego.concs)
        for _conc in concs_list[:-1]:
            result_str = result_str + regexfsm_to_str(_conc) + "|"
        result_str = "(" + result_str + regexfsm_to_str(concs_list[-1]) + ")"
    elif isinstance(_lego, conc):
        mults_list = list(_lego.mults)
        for _mult in mults_list:
            result_str = result_str + regexfsm_to_str(_mult)
    elif isinstance(_lego, mult):
        _multiplicand = _lego.multiplicand
        _multiplier = _lego.multiplier
        _min = str(_multiplier.min.v) if _multiplier.min.v!=0 else "0"
        _max = str(_multiplier.max.v) if _multiplier.max.v!=None else ""
        result_str = regexfsm_to_str(_multiplicand)
        if _min=="0" and _max=="":
            result_str = result_str + "*"
        elif _min==_max:
            if _min=="1":
                pass
            else:
                result_str = result_str + "{" + _min + "}"
        else:
            result_str = result_str + "{" + _min + "," + _max + "}"

    elif isinstance(_lego, charclass):
        chars = list(_lego.chars)
        if _lego.negated:
            if len(chars)==0:
                return "."
            result_str = "^"

        if for_grep:
            has_hyphen = False
            has_front_bracket = False
            has_back_bracket = False
            for c in chars:
                cc = c
                if c=="-":
                    has_hyphen = True
                    continue
                elif c=="[":
                    has_front_bracket = True
                    continue
                elif c=="]":
                    has_back_bracket = True
                    continue
                elif c=="`":
                    cc = "\\`"
                elif c=="\"":
                    cc = "\\\""
                elif c=="$": # grep -E "[${]" ./file will incur error
                    cc = "\\$"

                result_str = result_str + cc

            result_str = result_str + "-" if has_hyphen else result_str
            result_str = "[" + result_str if has_front_bracket else result_str
            result_str = "]" + result_str if has_back_bracket else result_str

        else:
            for c in chars:
                cc = c
                if c in "\\[]^-":
                    cc = "\\" + cc
                result_str = result_str + cc

        result_str = "[" + result_str + "]"

    return result_str



def find_extensible_legos(origin_pattern):
    origin_charclasses_parents = []
    origin_multipliers_parents = []

    _legos = [origin_pattern]
    while True:
        if len(_legos)==0:
            break

        if isinstance(_legos[0], pattern):
            concs_list = list(_legos[0].concs)
            for _conc in concs_list:
                _legos.append(_conc)
        elif isinstance(_legos[0], conc):
            mults_list = list(_legos[0].mults)
            for _mult in mults_list:
                _legos.append(_mult)
        elif isinstance(_legos[0], mult):
            _legos.append(_legos[0].multiplicand)
            _legos.append(_legos[0].multiplier)

            if isinstance(_legos[0].multiplicand, charclass):
                _charclass = _legos[0].multiplicand
                if not _charclass.negated:
                    if len(_charclass.chars)>1:
                        origin_charclasses_parents.append(_legos[0])
                else:
                    if len(_charclass.chars)!=0:
                        origin_charclasses_parents.append(_legos[0])
            if _legos[0].multiplier.min.v>0 or _legos[0].multiplier.max.v!=None: # this can be more stricter, that is, min!=max
                origin_multipliers_parents.append(_legos[0])
        elif isinstance(_legos[0], charclass):
            pass
        elif isinstance(_legos[0], multiplier):
            pass

        del _legos[0]

    return origin_charclasses_parents, origin_multipliers_parents


def create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index, invalid_patterns):
    if parent_index < len(origin_charclasses_parents): # deal with charclass
        parent_mult = origin_charclasses_parents[parent_index]
        origin_charclass = parent_mult.__dict__["multiplicand"]

        _chars = list(origin_charclass.chars)
        parent_mult.__dict__["multiplicand"] = charclass(_chars, not origin_charclass.negated)

        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # muted
        parent_mult.__dict__["multiplicand"] = origin_charclass
        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # non-muted
    elif parent_index >= len(origin_charclasses_parents)+len(origin_multipliers_parents): # copy
        cp_pattern = valid_pattern.copy()
        invalid_patterns.append(cp_pattern)
    else: # deal with multipliers
        parent_mult = origin_multipliers_parents[parent_index-len(origin_charclasses_parents)]
        origin_multiplier = parent_mult.__dict__["multiplier"]

        _max = origin_multiplier.max.v
        _min = origin_multiplier.min.v
        if _max!=None:
            parent_mult.__dict__["multiplier"] = multiplier.match("{" + str(_max+1) + ",}")[0]
        else:
            parent_mult.__dict__["multiplier"] = multiplier.match("{0," + str(_min) + "}")[0]

        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # muted
        parent_mult.__dict__["multiplier"] = origin_multiplier
        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # non-muted

    return


def create_invalid_regexes(valid_regex, breach_num=5):
    valid_pattern = parse(valid_regex)
    origin_charclasses_parents, origin_multipliers_parents = find_extensible_legos(valid_pattern)

    # find 10 extensible regexes
    try:
        chosen_num = random.sample(range(0, len(origin_charclasses_parents)), breach_num)
        origin_charclasses_parents = [origin_charclasses_parents[i] for i in range(0, len(origin_charclasses_parents)) if i in chosen_num]
    except:
        pass

    try:
        chosen_num = random.sample(range(0, len(origin_multipliers_parents)), breach_num)
        origin_multipliers_parents = [origin_multipliers_parents[i] for i in range(0, len(origin_multipliers_parents)) if i in chosen_num]
    except:
        pass


    invalid_legos = []
    create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, 0, invalid_legos)

    invalid_regexes = []
    for invalid_lego in invalid_legos:
        invalid_regexes.append(regexfsm_to_str(invalid_lego))

    print "len of invalid regexes : ", len(invalid_regexes)
    return invalid_regexes


def above_function_check():
    # test valid regexes are acceptable by re
    for _type, regex in valid_regexes.iteritems():
        try:
            prog = re.compile("^" + regex + "$")
        except:
            print "valid regex of " + _type + " is unacceptable by re"


    # test valid regexes after transtion are acceptable by re
    for _type, regex in valid_regexes.iteritems():
        try:
            test_str = regexfsm_to_str(parse(regex))
            print test_str
            prog = re.compile("^" + test_str + "$")
        except:
            print "valid regex of " + _type + " is unacceptable by re"


    for _type, valid_regex in valid_regexes.iteritems():
        print _type
        invalid_regexes = create_invalid_regexes(valid_regex, 5)

        for regex in invalid_regexes:
            try:
                prog = re.compile("^" + regex + "$")
            except:
                print "valid regex of " + _type + " is unacceptable by re"

    return

