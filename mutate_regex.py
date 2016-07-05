import re
from regexfsm.lego import *
import random
import string
from regex_mapping import mapping

valid_regexes = mapping


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

        if not origin_charclass.negated:
            _chars = list(origin_charclass.chars)
            chars_str = "".join(random.sample(_chars, len(_chars)/2))
            parent_mult.__dict__["multiplicand"] = charclass(chars_str, True)
        else:
            parent_mult.__dict__["multiplicand"] = charclass("", True) # . # no false negative??????

        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # muted
        parent_mult.__dict__["multiplicand"] = origin_charclass
        create_invalid_patterns(valid_pattern, origin_charclasses_parents, origin_multipliers_parents, parent_index+1, invalid_patterns) # non-muted
    elif parent_index >= len(origin_charclasses_parents)+len(origin_multipliers_parents): # copy
        cp_pattern = valid_pattern.copy()
        invalid_patterns.append(cp_pattern)
    else: # deal with multipliers
        parent_mult = origin_multipliers_parents[parent_index-len(origin_charclasses_parents)]
        origin_multiplier = parent_mult.__dict__["multiplier"]

        if origin_multiplier.max.v!=None:
            _max = origin_multiplier.max.v
            _min = origin_multiplier.min.v
            if _min==_max:
                parent_mult.__dict__["multiplier"] = multiplier.match("{" + str(_min+1) + ",}")[0]
            else:
                parent_mult.__dict__["multiplier"] = multiplier.match("{" + str((_min+_max+1)/2) + ",}")[0]
        else:
            _min = origin_multiplier.min.v
            _max = _min + 10
            parent_mult.__dict__["multiplier"] = multiplier.match("{0," + str(_max) + "}")[0]

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

