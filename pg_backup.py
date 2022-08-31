import pandas as pd
import csv
import re

# dataset = pd.read_csv('data/db/Rv41_KEN_data',
#                       sep=',',
#                       quotechar='"',
#                       skipinitialspace=True,
#                       quoting=csv.QUOTE_NONE,
#                       error_bad_lines=False,
#                       engine='python')

file1 = open('data/db/Rv41_KEN_data' , 'r', encoding="utf8")

# Using readlines()
lines = file1.readlines()
# print(len(lines))

count = 0
# Strips the newline character
for line in lines: #lines:
    if count<6:
        print("Line {}: {}".format(count, line.strip()))
        # if 912 <= count <= 924:
            # print(count,line)
        if len(line.split(",")) > 1:
            result = re.findall(r'"\([^"]*\)"', line)
            if result:
                print(result)
            # print(result[3])
            # print(result[4])
            # if result[0]:
            #     print(result)
            #     print(len(result))
        # comma_delimited = line.split(",")
        # print(comma_delimited)
        # print(comma_delimited[0])
        # print(len(comma_delimited))
        count += 1

file1.close()

