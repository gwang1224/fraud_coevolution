import json
import llmdetector as detector
import pandas as pd

# Question 1: Is llama3.2 able to accurately classify legit and fraudulent sequences?

error_seq = []
res = []

num_correct = 0
false_pos = 0
false_neg = 0
total_seq = 0

with open("data/coev_seq_v2.json", "r") as f:
    for line in f:

        total_seq += 1
        print(f"On sequence {total_seq}...")

        entry = json.loads(line.strip())
        id = entry['id']
        sequence = entry['sequence']
        label = entry['label']

        llm_label = detector.classify_sequence(sequence)

        if llm_label == entry['label']:
            num_correct += 1
        else:
            if llm_label == "fraud" and label == "legit":
                false_pos += 1
            if llm_label == "legit" and label == "fraud":
                false_neg += 1
            error_seq.append({
                'Sequence id': id,
                'Sequence': sequence,
                'Label': label,
                'LLM Generated Label': llm_label
            })
    
    df_error = pd.DataFrame(error_seq)
    print(df_error)
    df_error.to_csv("data/detector_full_errors.csv")

res.append({
    'Accuracy': num_correct/total_seq,
    'False positive': false_pos/total_seq,
    'False negative': false_neg/total_seq
})
df_res = pd.DataFrame(res)
print(df_res)
df_res.to_csv("data/detector_res_v2.csv")