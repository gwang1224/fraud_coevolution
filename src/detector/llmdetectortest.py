import json
import src.detector.llmdetector as detector
import pandas as pd
import time

error_seq = []
res = []

num_correct = 0
false_pos = 0
false_neg = 0
total_seq = 0
unclassifiable = 0

with open("data/coev_seq_v2.json", "r") as f:
    data = json.load(f)

    for id in data:
        total_seq += 1

        print(f"Classifying Sequence {id}.")
        label = data[id]['label']
        sequence = data[id]['sequence']

        classification, ___ = detector.ensemble_classify_sequence(sequence)

        if classification == label:
            num_correct += 1
        else:
            if classification == "fraud" and label == "legit":
                false_pos += 1
            if classification == "legit" and label == "fraud":
                false_neg += 1
            else: 
                unclassifiable += 1
            error_seq.append({
                'Sequence id': id,
                'Sequence': sequence,
                'Label': label,
                'LLM Generated Label': classification
            })
    
    df_error = pd.DataFrame(error_seq)
    print(df_error)
    df_error.to_csv("data/detector_errors_v2_2.csv")

res.append({
    'Accuracy': num_correct/total_seq,
    'False positive': false_pos/total_seq,
    'False negative': false_neg/total_seq,
    'Unclassifiable': unclassifiable
})
df_res = pd.DataFrame(res)
print(df_res)
df_res.to_csv("data/detector_res_v2_2.csv")