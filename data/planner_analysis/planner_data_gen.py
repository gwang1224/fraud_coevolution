"""
LLMPlanner data collection- 

Evaluation Metrics:
-------------------
(1) Sequence generated
(2) Attempts taken
(3) Run time
(4) Syntax Validity Score
    - % of steps that failed syntax validation
(5) Semantic Validity Score
    - % of steps that failed syntax validation
(6) Logical Coherence - (to be recorded manually)

Result: planner_res_v2.csv
"""

from ...src.utils import llmplanner
import utils.fraud_env as fraud_env
import csv
import json
import time

env_generator = fraud_env.FraudEnv()
env = env_generator.create_environment()
planner = llmplanner.LLMPlanner(env)

num_seq = 10

for i in range(num_seq):
    print(f"\n\n\nGenerating sequence {i} --------------------------------------------------------")
    start_time = time.time()

    sequence, attempts, syntax_errors, semantic_errors =  planner.generate_valid_fraud_seq(10)

    end_time = time.time()
    elapsed_time = end_time - start_time

    syn_err_per = syntax_errors/attempts
    sem_err_per = semantic_errors/attempts

    data = [[json.dumps(sequence), attempts, elapsed_time, syn_err_per, sem_err_per]]
    print(data)


    with open('fraud_planner_v4.csv', 'a', newline='') as file:
        writer= csv.writer(file)
        writer.writerows(data)
        