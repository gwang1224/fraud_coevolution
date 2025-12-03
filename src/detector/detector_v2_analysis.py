import csv
import llmdetector

with open("data/detector/v2/detector_errors_v2_3.csv", mode='r',) as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        print(row[2])
        print(llmdetector.explain_classification(row[2]))
        print("---------------------------------------------------------------")