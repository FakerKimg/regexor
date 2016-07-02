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
    condense_types = ["simplybfs", "simplydfs", "allcoverbfs", "allcoverdfs"]


    # generate invalid graph, generate test patterns and write into file
    for input_type in input_types:
        result_patterns = {}
        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                print filename + " generating patterns"
                _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type)
                output_patterns(filename, _ggg, output_paths, len(output_paths))
                result_patterns[filename] = (_ggg, output_paths)


    results = {}
    for input_type in input_types:
        # generate testers and record them
        exploitable_regexes = create_invalid_regexes(mapping[input_type], tester_num)
        with open("./test_patterns/"+input_type+".testers", "w") as trf:
            for exploitable_regex in exploitable_regexes:
                trf.write(exploitable_regex)
                trf.write("\n")
            trf.close()
        # start to test each pattern
        for scc_type in scc_types:
            for condense_type in condense_types:
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
                for i in range(0, len(exploitable_regexes)):
                    try:
                        cmd_line = ["grep", "-E", "\"^"+exploitable_regexes[i]+"$\"", "./test_patterns/"+filename]
                        cmd_line = [" ".join(cmd_line)]
                        result = subprocess.check_output(cmd_line, shell=True)
                        if result!="":
                            exploit_count = exploit_count + 1
                            for pass_case in result.split("\n")[:-1]:
                                try:
                                    utf8case = pass_case.encode("utf-8")
                                    test_cases_matching[utf8case].add(i)
                                except:
                                    print "no key ??????????"
                                    import pdb;pdb.set_trace()
                    except Exception as e:
                        if e.returncode==1 and e.output=="": # match empty
                            pass
                        else:
                            print "error occurs when using \"" + cmd_line[0]  + "\""
                            import pdb;pdb.set_trace()



                # statistic
                unused_count = 0
                exploit_sets = test_cases_matching.values()
                issub_list = [0]*len(exploit_sets)
                for i in range(0, len(exploit_sets)):
                    if len(exploit_sets[i])==0:
                        unused_counit = unused_count + 1
                    if issub_list[i]==1:
                        continue

                    for j in range(0, len(exploit_sets)):
                        if i==j:
                            continue
                        if exploit_sets[i].issubset(exploit_sets[j]):
                            issub_list[i] = 1

                issub_sets = [i for i in issub_list if i==1]

                print filename + " statisticing"
                print [exploit_count, len(exploitable_regexes), unused_count, len(issub_sets), len(test_cases_matching.keys())]
                results[filename] = [exploit_count, len(exploitable_regexes), unused_count, len(issub_sets), len(test_cases_matching.keys())]


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
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
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



