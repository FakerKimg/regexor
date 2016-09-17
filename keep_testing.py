from data_tester import *


def keep_testing():
    input_types = ["tel", "url", "email", "date", "time", "number", "range", "color"]
    scc_types = ["shortest", "all-vertices-covered", "tripartie"]
    condense_types = ["simplybfs", "simplydfs", "allcoverbfs", "allcoverdfs"]

    _patterns = {}
    for input_type in input_types:
        for scc_type in scc_types:
            for condense_type in condense_types:
                filename = input_type + "." + scc_type + "." + condense_type + ".invalids"
                _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type, False)
                _patterns[filename] = {"graph": _ggg, "output_paths": output_paths}

                filename = input_type + "." + scc_type + "." + condense_type + ".valids"
                _ggg, output_paths = generate_patterns(input_type, scc_type, condense_type, True)
                _patterns[filename] = {"graph": _ggg, "output_paths": output_paths}

    i = 3
    while True:
        test_once(_patterns, i)
        i = i + 1
        if i==6:
            i = 3

    return


keep_testing()

