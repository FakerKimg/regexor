from pattern_generator import *
import re
import string
from mutate_regex import *
from regexfsm.lego import *
import subprocess
import os
import time
import datetime
import shutil
import math

def test_once(tester_num=5):

    mapping = {
        "tel": "((\((0|\+886)2\)[0-9]{4}-[0-9]{4})|((0|\+886)9[0-9]{8}))",
        "url": "[A-Za-z][A-Za-z0-9+\-.]*:(?://(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9A-Fa-f]{1,4}:){6}|::(?:[0-9A-Fa-f]{1,4}:){5}|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,1}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}|(?:(?:[0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}|(?:(?:[0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:|(?:(?:[0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})?::)(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})?::)|[Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*)(?::[0-9]*)?(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*|/(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?|((?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?)(?:\?(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?(#(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?",
        "email": "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*",
        "date": "(([1-9]*[0-9]{4,}-(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|([1-9]*[0-9]{4,}-(0[13456789]|1[012])-(0[1-9]|[12][0-9]|30))|([1-9]*[0-9]{4,}-02-(0[1-9]|1[0-9]|2[0-8]))|([1-9]*([13579][26]|[02468][048])00-02-29)|([1-9]*[0-9]{2}([13579][26]|[2468][048]|04|08)-02-29))",
        "time": "([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9](.[0-9]{1,3})?)?",
        "number": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
        "range": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
        "color": "#[0-9a-fA-F]{6}",
    }


    input_types = ["tel", "url", "email", "date", "time", "number", "range", "color"]
    scc_types = ["shortest", "all-vertices-covered", "tripartie"]
    condense_types = ["shortest", "simplybfs", "simplydfs", "allcoverbfs", "allcoverdfs"]

    for input_type in input_types:
        output_pathss = {}
        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                print filename
                _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type, False)
                output_pathss[filename] = (_ggg, output_paths)

        for fn, obj in output_pathss.iteritems():
            output_patterns(fn, obj[0], obj[1], len(obj[1]))


        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".valids"
                print filename
                _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type, True)
                output_pathss[filename] = (_ggg, output_paths)

        for fn, obj in output_pathss.iteritems():
            output_patterns(fn, obj[0], obj[1], len(obj[1]))


    results = {}
    for input_type in input_types:
        exploitable_regexes = create_invalid_regexes(mapping[input_type], tester_num)
        for scc_type in scc_types:
            for condense_type in condense_types:
                # invalid cases
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                invalid_cases_count = 0
                invalid_cases_matching = {}
                with open("./test_patterns/"+filename, "r") as test_file:
                    for line in test_file:
                        utf8line = line[:-1].encode("utf-8") if line[-1]=='\n' else line
                        invalid_cases_matching.setdefault(utf8line, set())
                        invalid_cases_count = invalid_cases_count + 1
                    test_file.close()

                false_positive = 0
                i = 0
                for exploitable_regex in exploitable_regexes:
                    try:
                        cmd_line = ["grep", "-E", "\"^"+exploitable_regex+"$\"", "./test_patterns/"+filename]
                        cmd_line = [" ".join(cmd_line)]
                        result = subprocess.check_output(cmd_line, shell=True)
                        if result!="":
                            false_positive = false_positive + 1
                            for pass_case in result.split("\n")[:-1]:
                                utf8case = pass_case.encode("utf-8")
                                invalid_cases_matching[utf8case].add(i)

                    except Exception as e:
                        if e.returncode==1 and e.output=="": # match empty
                            pass
                            #print "wrong again?????"
                        else:
                            print "error occurs when using \"" + " ".join(cmd_line) + "\""

                    i = i + 1


                # valid cases
                filename = input_type + "." + scc_type + "." + condense_type + ".valids"
                valid_cases_count = 0
                valid_cases_matching = {}
                with open("./test_patterns/"+filename, "r") as test_file:
                    for line in test_file:
                        utf8line = line[:-1].encode("utf-8") if line[-1]=='\n' else line
                        valid_cases_matching.setdefault(utf8line, set())
                        valid_cases_count = valid_cases_count + 1
                    test_file.close()

                false_negative = 0
                i = 0
                for exploitable_regex in exploitable_regexes:
                    try:
                        cmd_line = ["grep", "-E", "\"^"+exploitable_regex+"$\"", "./test_patterns/"+filename]
                        cmd_line = [" ".join(cmd_line)]
                        result = subprocess.check_output(cmd_line, shell=True)
                        resultss = result.split("\n")[:-1]

                    except Exception as e:
                        if e.returncode==1 and e.output=="": # match empty
                            resultss = []
                        else:
                            print "error occurs when using \"" + " ".join(cmd_line) + "\""

                    if len(resultss)!=valid_cases_count:
                        false_negative = false_negative + 1
                        for pass_case in resultss:
                            utf8case = pass_case.encode("utf-8")
                            valid_cases_matching[utf8case].add(i)

                    i = i + 1


                # redundancy calculation

                invalid_unused_count = 0
                sets = invalid_cases_matching.values()
                issub_list = [0]*len(sets)
                for i in range(0, len(sets)):
                    if len(sets[i])==0:
                        invalid_unused_count = invalid_unused_count + 1

                    if issub_list[i]==1:
                        continue

                    for j in range(0, len(sets)):
                        if i==j:
                            continue
                        if sets[i].issubset(sets[j]):
                            issub_list[i] = 1
                            break


                invalid_sub_sets = [i for i in issub_list if i==1]


                valid_unused_count = 0
                sets = valid_cases_matching.values()
                issub_list = [0]*len(sets)
                for i in range(0, len(sets)):
                    if len(sets[i])==0:
                        valid_unused_count = valid_unused_count + 1

                    if issub_list[i]==1:
                        continue

                    for j in range(0, len(sets)):
                        if i==j:
                            continue
                        if sets[i].issubset(sets[j]):
                            issub_list[i] = 1
                            break

                valid_sub_sets = [i for i in issub_list if i==1]


                print input_type + "." + scc_type + "." + condense_type
                print [len(exploitable_regexes), false_positive, invalid_cases_count, invalid_unused_count, len(invalid_sub_sets), false_negative, valid_cases_count, valid_unused_count, len(valid_sub_sets)]
                #results[input_type + "." + scc_type + "." + condense_type] = [exploit_count, len(exploitable_regexes), unused_count, len(sub_sets), cases_count]
                results[input_type + "." + scc_type + "." + condense_type] = [len(exploitable_regexes), false_positive, invalid_cases_count, invalid_unused_count, len(invalid_sub_sets), false_negative, valid_cases_count, valid_unused_count, len(valid_sub_sets)]







    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir("./evaluation_patterns/" + st)

    for input_type in input_types:
        csvf = open("./evaluation_patterns/"+input_type+"_results.csv", "a")
        csvf.write("\n")
        csvf.write(st)
        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".valids"
                shutil.copyfile("./test_patterns/"+filename, "./evaluation_patterns/" + st + "/" +filename)
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                shutil.copyfile("./test_patterns/"+filename, "./evaluation_patterns/" + st + "/" +filename)

                for vvv in results[input_type + "." + scc_type + "." + condense_type]:
                    csvf.write(",")
                    csvf.write(str(vvv))
    
        csvf.close()

    """
    with open("./evaluation_patterns/"+st+"/evaluation_result", "w") as rf:
        json_str = json.dumps(results)
        rf.write(json_str)
        rf.close()
    """



