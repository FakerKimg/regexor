input_types = ["tel", "url", "email", "date", "time", "number", "range", "color"]
scc_types = ["shortest", "fakesaleman", "radiation"]
condense_types = ["simplybfs", "allbranch", "allcover"]

for input_type in input_types:
    csvf = open("./evaluation_patterns/"+input_type+"_results.csv", "w")
    csvf.write("timestamp")
    for scc_type in scc_types:
        for condense_type in condense_types:
            csvf.write(",")
            csvf.write(scc_type+"+"+condense_type)
            csvf.write(",")
    csvf.write("\n")
    csvf.close()

