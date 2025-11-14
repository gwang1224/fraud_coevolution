import fraud_env as env
import llmplanner
import pydantic_syntax as eval
import random
import json

def add_banks(env):
    env.add_node_with_attribute("bankofamerica", "bank")
    env.add_node_with_attribute("chase", "bank")
    env.add_node_with_attribute("firstfinancial", "bank")
    env.add_node_with_attribute("wellsfargo", "bank")
    env.add_node_with_attribute("citibank", "bank")

def add_participants(env):
    env.add_node_with_attribute("sally", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_sally", "account", {"owner": "sally", "bank": "bankofamerica", "balance": 6000.00})
    env.add_node_with_attribute("grace", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_grace", "account", {"owner": "grace", "bank": "chase", "balance": 400000.00})
    env.add_node_with_attribute("bill", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_bill", "account", {"owner": "bill", "bank": "firstfinancial", "balance": 15000.00})
    env.add_node_with_attribute("olivia", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_olivia", "account", {"owner": "olivia", "bank": "wellsfargo", "balance": 8500.00})
    env.add_node_with_attribute("james", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_james", "account", {"owner": "james", "bank": "citibank", "balance": 20000.00})
    env.add_node_with_attribute("nina", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_nina", "account", {"owner": "nina", "bank": "wellsfargo", "balance": 12000.00})

def add_organizations(env):
    env.add_node_with_attribute("ConEdison", "participant", {"role": "utility", "isFraudster": False})
    env.add_node_with_attribute("acc_conedison", "account", {"owner": "ConEdison", "bank": "bankofamerica", "balance": 300000.00})
    env.add_node_with_attribute("TMobile", "participant", {"role": "telecom", "isFraudster": False})
    env.add_node_with_attribute("acc_tmobile", "account", {"owner": "TMobile", "bank": "chase", "balance": 500000.00})
    env.add_node_with_attribute("BlueDiner", "participant", {"role": "restaurant", "isFraudster": False})
    env.add_node_with_attribute("acc_bluediner", "account", {"owner": "BlueDiner", "bank": "firstfinancial", "balance": 80000.00})
    env.add_node_with_attribute("WellesleyCollege", "participant", {"role": "institution", "isFraudster": False})
    env.add_node_with_attribute("acc_wellesley", "account", {"owner": "WellesleyCollege", "bank": "bankofamerica", "balance": 1000000.00})

def add_fraudsters(env):
    env.add_node_with_attribute("govco", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_govco", "account", {"owner": "govco", "bank": "citibank", "balance": 0.00})
    env.add_node_with_attribute("insuranceco", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_insuranceco", "account", {"owner": "insuranceco", "bank": "bankofamerica", "balance": 0.00})
    env.add_node_with_attribute("insurancenet", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_insurancenet", "account", {"owner": "insurancenet", "bank": "chase", "balance": 0.00})
    env.add_node_with_attribute("fishmaster", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_fishmaster", "account", {"owner": "fishmaster", "bank": "firstfinancial", "balance": 0.00})

def generate_sequences(env, planner, data_len=100, num_fraud_seq=20):
    fraud_ind = random.sample(range(0, data_len), num_fraud_seq)
    with open("sequences2.json", "w") as f:
        for i in range(data_len):
            print(i)
            label = "fraud" if i in fraud_ind else "legit"

            T = None
            while T is None:
                seq = planner.generate_sequence(label)
                try:
                    T = eval.SequenceModel.model_validate(seq, context={"entities": env.get_nodes()})
                except Exception:
                    continue

            data = {
                "id": i,
                "label": label,
                "sequence": seq['sequence']
            }
            f.write(json.dumps(data) + "\n")


if __name__ == "__main__":
    env_instance = env.FraudEnv()
    add_banks(env_instance)
    add_participants(env_instance)
    add_organizations(env_instance)
    add_fraudsters(env_instance)

    planner = llmplanner.LLMPlanner(env_instance)
    generate_sequences(env_instance, planner)
