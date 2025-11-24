"""
Data Collection llmplanner V2

Evaluation Metrics:
-------------------
(1) Sequence generated
(2) Attempts taken
(3) Run time
(4) Syntax Validity Score
    - % of steps that failed syntax validation
(5) Semantic Validity Score
    - % of steps that failed syntax validation
(6) Logical Coherence - recorded manually

Planner given 10 maximum attempts
"""

import llmplanner
import environment
import fraud_env
import csv
import json
import time

env1 = fraud_env.FraudEnv()
env = environment.create_environment(env1)
planner = llmplanner.LLMPlanner(env)

num_seq = 50

for i in range(num_seq):
    time.sleep(120)
    print(f"Generating sequence {i} --------------------------------------------------------")
    start_time = time.time()

    sequence, attempts, syntax_errors, semantic_errors =  planner.generate_valid_fraud_seq(10)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(syntax_errors)
    print(semantic_errors)

    syn_err_per = syntax_errors/attempts
    sem_err_per = semantic_errors/attempts

    data = [[json.dumps(sequence), attempts, elapsed_time, syn_err_per, sem_err_per]]
    print(data)


    with open('fraud_planner_v2.csv', 'a', newline='') as file:
        writer= csv.writer(file)
        writer.writerows(data)
        