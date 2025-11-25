import fraud_env
import llmplanner_v3 as llmplanner
import random
import json
import time

env_generator = fraud_env.FraudEnv()
env = env_generator.create_environment()
planner = llmplanner.LLMPlanner(env)


def generate_sequences(env, planner, data_len=100, num_fraud_seq=50):
    fraud_ind = random.sample(range(0, data_len), num_fraud_seq)
    with open("coev_seq_v2.json", "w") as f:
        for i in range(data_len):
            print(f"Sequence {i} ---------------------------------------------")
            label = "fraud" if i in fraud_ind else "legit"
            
            seq = None

            while not seq:
                time.sleep(10)
                if label == "fraud": seq, __, __, __ = planner.generate_valid_fraud_seq()
                else: seq = planner.generate_valid_legit_seq()

            data = {
                "id": i,
                "label": label,
                "sequence": seq['sequence']
            }
            f.write(json.dumps(data) + ",\n")


if __name__ == "__main__":
    generate_sequences(env, planner)
