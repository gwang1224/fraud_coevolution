import utils.fraud_env as fraud_env
import llmplanner as llmplanner
import random
import json
import time

env_generator = fraud_env.FraudEnv()
env = env_generator.create_environment()
planner = llmplanner.LLMPlanner(env)


def generate_sequences(env, planner, data_len=4, num_fraud_seq=2):
    data = {}
    fraud_ind = random.sample(range(0, data_len), num_fraud_seq)

    for i in range(data_len):
        time.sleep(30)
        print(f"Sequence {i} ---------------------------------------------")
        label = "fraud" if i in fraud_ind else "legit"

        seq = None

        while not seq:
            if label == "fraud": seq, __, __, __ = planner.generate_valid_fraud_seq(5)
            else: seq = planner.generate_valid_legit_seq(5)

        data[i] = {
            "label": label,
            "sequence": seq['sequence']
        }
    
        with open("/data/coev/coev_gen1.csv", 'w') as json_file:
            json.dump(data, json_file, indent=4)



if __name__ == "__main__":
    generate_sequences(env, planner)
