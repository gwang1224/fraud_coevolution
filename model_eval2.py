"""
Model Evaluation Script

Description:
-------------
Evaluates multiple LLMs for their ability to generate valid FAST payment fraud sequences
using the LLMPlanner class from llmplanner.py. It runs multiple samples for each model,
validates the output, and logs performance statistics.

Evaluation Metrics:
-------------------
(1) Valid Sequences - number of sequences that pass syntax and semantic validation.
(2) Average Attempts - Average number of attempts
(3) Error Sequences

Current Models:
---------------
- chevalblanc/gpt-4o-mini
- llama3.2
- mistral
- gemma3:4b

Outputs:
--------
- Prints progress and model statistics to console.
- Saves summary table to "model_eval_results2.csv" in the working directory.
"""

import pandas as pd
import llmplanner
import environment
import fraud_env

env1 = fraud_env.FraudEnv()
env = environment.create_environment(env1)
planner = llmplanner.LLMPlanner(env)

# Models to test
models = ['llama3.2', 'mistral','gemma3:4b']

samples = 10
results = []

for model in models:
    print(f"Testing {model}")
    print("-" * 80)

    valid_count = 0
    total_attempts = 0
    invalid_count = 0
    
    for i in range(samples):
        print(f"Generating sequence {i}...")

        sequence, attempts =  planner.generate_valid_fraud_seq()
        print(sequence)
        if sequence is not None:
            valid_count += 1
            total_attempts += attempts
        if sequence is None:
            invalid_count += 1

    if total_attempts > 0:
        average_attempts = total_attempts/valid_count        

    results.append({
        'Model': model,
        'Valid Count': valid_count,
        'Invalid Count': invalid_count,
        'Total Samples': samples,
        'Average attempts': average_attempts
    })

df = pd.DataFrame(results)
print(df)
df.to_csv("model_eval_results2.csv", index=False)

# import csv

# data = [
#     ['Name', 'Age', 'City'],
#     ['Alice', 30, 'New York'],
#     ['Bob', 24, 'London']
# ]

# with open('people.csv', 'a', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(data)