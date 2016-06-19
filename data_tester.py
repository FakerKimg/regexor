from pattern_generator import *


filename = "email.shortest.simplybfs.pattern"

generate_pattern(filename)

with open("email.shortest.simplybfs.pattern", "r") as data_file:
    test_data = []
    for line in data_file:
        test_data.append(line)

    data_file.close()






