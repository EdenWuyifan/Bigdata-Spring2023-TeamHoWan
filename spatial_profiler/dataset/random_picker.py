import argparse
import csv
import random

"""random_picker.py
Author: Eden Wu
Example: python3 random_picker.py --path x.csv 10000
        Random sample 10000 lines out of csv into output.csv
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--path', help='input file path')
    parser.add_argument('size', help='output file size', type=int)
    args = parser.parse_args()

    TEST_DATA_LINES = args.size
    with open(args.path, mode="r") as file:
        countFile = csv.reader(file)
        count = sum(1 for _ in countFile)
    # opening the CSV file
    with open(args.path, mode="r") as file, open("./sample.csv", mode="w") as test:
        # reading the CSV file
        testFile = csv.writer(test)
        csvFile = csv.reader(file)
        header = next(csvFile)
        print(header)
        testFile.writerow(header)
        # displaying the contents of the CSV file
        random_picks = random.sample(range(count), TEST_DATA_LINES)
        for index, row in enumerate(csvFile):
            if index in random_picks:
                testFile.writerow(row)
