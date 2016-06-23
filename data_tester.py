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
scc_types = ["shortest", "fakesaleman", "radiation"]
condense_types = ["simplybfs", "allbranch", "allcover"]


results = {}
for input_type in input_types:
    for scc_type in scc_types:
        for condense_type in condense_types:
            filename = input_type + "." + scc_type + "." + condense_type + ".patterns"
            print filename
            _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type)
            output_patterns(filename, _ggg, output_paths, 1)

            exploitable_regexes = create_invalid_regexes(mapping[input_type], 5)
            exploit_count = 0
            for exploitable_regex in exploitable_regexes:
                try:
                    cmd_line = ["grep", "-E", "\"^"+exploitable_regex+"$\"", "./test_patterns/"+filename]
                    cmd_line = [" ".join(cmd_line)]

                    """
                    ppp = os.popen(" ".join(cmd_line), "r")
                    if ppp.readline()!="":
                        exploit_count = exploit_count + 1
                    """

                    result = subprocess.check_output(cmd_line, shell=True)
                    if result!="":
                        exploit_count = exploit_count + 1

                except Exception as e:
                    if e.returncode==1 and e.output=="": # match empty
                        pass
                        #print "wrong again?????"
                    else:
                        import pdb;pdb.set_trace()
                        print "error occurs when using \"" + " ".join(cmd_line) + "\""

            print (exploit_count, len(exploitable_regexes))
            results[filename] = list((exploit_count, len(exploitable_regexes)))

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
os.mkdir("./evaluation_patterns/" + st)


for input_type in input_types:
    for scc_type in scc_types:
        for condense_type in condense_types:
            filename = input_type + "." + scc_type + "." + condense_type + ".patterns"
            shutil.copyfile("./test_patterns/"+filename, "./evaluation_patterns/" + st + "/" +filename)

with open("./evaluation_patterns/"+st+"/evaluation_result", "w") as rf:
    json_str = json.dumps(results)
    rf.write(json_str)
    rf.close()



