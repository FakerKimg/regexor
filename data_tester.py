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

def test_once(_patterns, tester_num=5):

    mapping = {
        "tel": "((\((0|\+886)2\)[0-9]{4}-[0-9]{4})|((0|\+886)9[0-9]{8}))",
        "url": "[A-Za-z][A-Za-z0-9+\-.]*:(?://(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:]|%[0-9A-Fa-f]{2})*@)?(?:\[(?:(?:(?:(?:[0-9A-Fa-f]{1,4}:){6}|::(?:[0-9A-Fa-f]{1,4}:){5}|(?:[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,1}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){3}|(?:(?:[0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})?::(?:[0-9A-Fa-f]{1,4}:){2}|(?:(?:[0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}:|(?:(?:[0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})?::)(?:[0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{1,4}|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))|(?:(?:[0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})?::[0-9A-Fa-f]{1,4}|(?:(?:[0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})?::)|[Vv][0-9A-Fa-f]+\.[A-Za-z0-9\-._~!$&'()*+,;=:]+)\]|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-Za-z0-9\-._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})*)(?::[0-9]*)?(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*|/(?:(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?|((?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})+(?:/(?:[A-Za-z0-9\-._~!$&'()*+,;=:@]|%[0-9A-Fa-f]{2})*)*)?)(?:\?(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?(#(?:[A-Za-z0-9\-._~!$&'()*+,;=:@/?]|%[0-9A-Fa-f]{2})*)?",
        "email": "[a-zA-Z0-9.!#$%&'*+/=?\^_`{|}~\-]+@[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*",
        "date": "(([1-9]*[0-9]{4,}-(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|([1-9]*[0-9]{4,}-(0[13456789]|1[012])-(0[1-9]|[12][0-9]|30))|([1-9]*[0-9]{4,}-02-(0[1-9]|1[0-9]|2[0-8]))|([1-9]*([13579][26]|[02468][048])00-02-29)|([1-9]*[0-9]{2}([13579][26]|[2468][048]|04|08)-02-29))",
        "time": "([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9](\.[0-9]{1,3})?)?",
        "number": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
        "range": "[\-+]?[0-9]*(\.[0-9]*)?([eE][\-+]?[0-9]*)?",
        "color": "#[0-9a-fA-F]{6}",
    }

    input_types = ["tel", "url", "email", "date", "time", "number", "range", "color"]
    scc_types = ["shortest", "all-vertices-covered", "tripartie"]
    condense_types = ["simplybfs", "simplydfs", "allcoverbfs", "allcoverdfs"]


    for input_type in input_types:
        for scc_type in scc_types:
            for condense_type in condense_types:
                # generate invalid graph, generate test patterns and write into file
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                output_patterns(filename, _patterns[filename]["graph"], _patterns[filename]["output_paths"], len(_patterns[filename]["output_paths"]))

                # generate invalid graph, generate test patterns and write into file
                filename = input_type + "." + scc_type + "." + condense_type + ".valids"
                output_patterns(filename, _patterns[filename]["graph"], _patterns[filename]["output_paths"], len(_patterns[filename]["output_paths"]))

    results = {}
    for input_type in input_types:
        # generate testers and record them
        test_valid_regexes = create_invalid_regexes(mapping[input_type], True, tester_num)
        test_invalid_regexes = create_invalid_regexes(mapping[input_type], False, tester_num)

        # start to test each invalid pattern
        for scc_type in scc_types:
            for condense_type in condense_types:
                # start to test each invalid pattern
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"

                #cases_count = 0 replaced with len(test_cases_matching.keys())
                test_cases_matching = {}
                with open("./test_patterns/"+filename, "r") as test_file:
                    for line in test_file:
                        utf8line = line[:-1] if line[-1]=="\n" else line
                        utf8line = utf8line.encode("utf-8")
                        assert(utf8line!="")
                        test_cases_matching.setdefault(utf8line, set())
                    test_file.close()

                # check whether our invalid patterns could exploit testers
                exploit_count = 0
                for i in range(0, len(test_invalid_regexes)):
                    try:
                        cmd_line = ["grep", "-E", "\"^"+test_invalid_regexes[i]+"$\"", "./test_patterns/"+filename]
                        cmd_line = [" ".join(cmd_line)]
                        result = subprocess.check_output(cmd_line, shell=True)
                        if result!="":
                            exploit_count = exploit_count + 1
                            for pass_case in result.split("\n")[:-1]:
                                utf8case = pass_case.encode("utf-8")
                                test_cases_matching[utf8case].add(i)
                    except Exception as e:
                        if e.returncode==1 and e.output=="": # match empty
                            pass
                        else:
                            print "error occurs when using \"" + cmd_line[0]  + "\""
                            import pdb;pdb.set_trace()





                # start to test each valid pattern
                filename = input_type + "." + scc_type + "." + condense_type + ".valids"

                #cases_count = 0 replaced with len(test_cases_matching.keys())
                test_cases_not_matching = {}
                with open("./test_patterns/"+filename, "r") as test_file:
                    for line in test_file:
                        utf8line = line[:-1] if line[-1]=="\n" else line
                        utf8line = utf8line.encode("utf-8")
                        assert(utf8line!="")
                        test_cases_not_matching.setdefault(utf8line, set())
                    test_file.close()

                # check whether our valid patterns could find problem testers
                valid_cases = test_cases_not_matching.keys()
                find_count = 0
                for i in range(0, len(test_valid_regexes)):
                    try:
                        cmd_line = ["grep", "-E", "\"^"+test_valid_regexes[i]+"$\"", "./test_patterns/"+filename]
                        cmd_line = [" ".join(cmd_line)]
                        result = subprocess.check_output(cmd_line, shell=True)
                        if result!="":
                            found = False
                            result_patterns = [pattern.encode("utf-8") for pattern in result.split("\n")[:-1]]
                            for valid_case in valid_cases:
                                if valid_case not in result_patterns:
                                    found = True
                                    test_cases_not_matching[valid_case].add(i)
                            find_count = find_count + 1 if found else find_count
                    except Exception as e:
                        if e.returncode==1 and e.output=="": # match empty
                            find_count = find_count + 1
                            for valid_case in valid_cases:
                                test_cases_not_matching[valid_case].add(i)
                        else:
                            print "error occurs when using \"" + cmd_line[0]  + "\""
                            import pdb;pdb.set_trace()





                # invalid statistic
                invalid_unused_count = 0
                exploit_sets = test_cases_matching.values()
                invalid_issub_list = [0]*len(exploit_sets)
                for i in range(0, len(exploit_sets)):
                    if len(exploit_sets[i])==0:
                        invalid_unused_counit = invalid_unused_count + 1
                    if invalid_issub_list[i]==1:
                        continue

                    for j in range(0, len(exploit_sets)):
                        if i==j:
                            continue
                        if exploit_sets[i].issubset(exploit_sets[j]):
                            invalid_issub_list[i] = 1

                invalid_issub_sets = [i for i in invalid_issub_list if i==1]

                # valid statistic
                valid_unused_count = 0
                find_sets = test_cases_not_matching.values()
                valid_issub_list = [0]*len(find_sets)
                for i in range(0, len(find_sets)):
                    if len(find_sets[i])==0:
                        valid_unused_counit = valid_unused_count + 1
                    if valid_issub_list[i]==1:
                        continue

                    for j in range(0, len(find_sets)):
                        if i==j:
                            continue
                        if find_sets[i].issubset(find_sets[j]):
                            valid_issub_list[i] = 1

                valid_issub_sets = [i for i in valid_issub_list if i==1]



                print filename + " statisticing"
                print [exploit_count, find_count, len(test_invalid_regexes), invalid_unused_count, valid_unused_count, len(invalid_issub_sets), len(valid_issub_sets), len(test_cases_matching.keys()),  len(test_cases_not_matching.keys())]
                filename = input_type + "." + scc_type + "." + condense_type + ".patterns"
                results[filename] = [exploit_count, find_count, len(test_invalid_regexes), invalid_unused_count, valid_unused_count, len(invalid_issub_sets), len(valid_issub_sets), len(test_cases_matching.keys()),  len(test_cases_not_matching.keys())]


















    # record statistic
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir("./evaluation_patterns/" + st)

    for input_type in input_types:
        csvf = open("./evaluation_patterns/"+input_type+"_results.csv", "a")
        csvf.write("\n")
        csvf.write(st)
        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".testers"
                shutil.copyfile("./test_patterns/"+filename, "./evaluation_patterns/" + st + "/" +filename)
                shutil.copyfile("./test_patterns/"+input_type+".testers", "./evaluation_patterns/"+st+"/"+input_type+".testers")

                for value in results[filename]:
                    csvf.write(",")
                    csvf.write(str(value))
        csvf.close()

    """
    with open("./evaluation_patterns/"+st+"/evaluation_result", "w") as rf:
        json_str = json.dumps(results)
        rf.write(json_str)
        rf.close()
    """



