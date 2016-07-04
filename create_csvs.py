import sys

input_types = ["tel", "url", "email", "date", "time", "number", "range", "color"]
scc_types = ["shortest", "all-vertices-covered", "tripartie"]
condense_types = ["simplybfs", "simplydfs", "allcoverbfs", "allcoverdfs"]


value_num = 9

for input_type in input_types:
    csvf = open("./evaluation_patterns/"+input_type+"_results.csv", "w")
    csvf.write("timestamp")
    for scc_type in scc_types:
        for condense_type in condense_types:
            csvf.write(",")
            csvf.write(scc_type+"+"+condense_type)
            for i in range(0, value_num-1):
                csvf.write(",")
    csvf.write("\n")
    csvf.close()

