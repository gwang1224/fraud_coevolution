import fraud_env
import llmplanner
import pydantic_syntax as eval
import random
import json


env = fraud_env.FraudEnv()

# Add banks
env.add_node_with_attribute("BankOfAmerica", "bank")
env.add_node_with_attribute("bankofamerica", "bank")
env.add_node_with_attribute("chase", "bank")
env.add_node_with_attribute("firstfinancial", "bank")

# Add individuals
env.add_node_with_attribute("sally", "individual")
env.add_node_with_attribute("grace", "individual")
env.add_node_with_attribute("bill", "individual")

# Add fraudsters
env.add_node_with_attribute("scamgov", "fraudster", {"status": "active", "description": "Impersonates gov for SID"})
env.add_node_with_attribute("scamco", "fraudster", {"status": "active", "description": "Impersonates gov for SID"})

# Add accounts (using valid banks)
env.add_node_with_attribute("acc_sally", "account", {"owner": "sally", "bank": "BankOfAmerica", "balance": 6000.00})
env.add_node_with_attribute("acc_grace", "account", {"owner": "grace", "bank": "Chase", "balance": 400000.00})
env.add_node_with_attribute("acc_scamgov", "account", {"owner": "scamgov", "bank": "FirstFinancial", "balance": 0.00})

# Add ownership edges
env.add_ownership_edge("sally", "acc_sally")
env.add_ownership_edge("grace", "acc_grace")
env.add_ownership_edge("scamgov", "acc_scamgov")

# --- ADDITIONAL ENTITIES ---

# Add banks
env.add_node_with_attribute("WellsFargo", "bank")
env.add_node_with_attribute("Citibank", "bank")

# Add individuals
env.add_node_with_attribute("olivia", "individual", {"role": "individual"})
env.add_node_with_attribute("james", "individual", {"role": "individual"})
env.add_node_with_attribute("nina", "individual", {"role": "individual"})

# Add legitimate businesses / organizations
env.add_node_with_attribute("ConEdison", "individual", {"role": "utility"})
env.add_node_with_attribute("TMobile", "individual", {"role": "telecom"})
env.add_node_with_attribute("BlueDiner", "individual", {"role": "restaurant"})
env.add_node_with_attribute("WellesleyCollege", "individual", {"role": "institution"})

# Add fraudsters
env.add_node_with_attribute("fraudnet", "fraudster", {"status": "active", "description": "Operates tech support scams"})
env.add_node_with_attribute("phishmaster", "fraudster", {"status": "active", "description": "Phishing campaigns targeting elderly"})

# Add accounts (linked to banks)
env.add_node_with_attribute("acc_olivia", "account", {"owner": "olivia", "bank": "WellsFargo", "balance": 8500.00})
env.add_node_with_attribute("acc_james", "account", {"owner": "james", "bank": "Citibank", "balance": 20000.00})
env.add_node_with_attribute("acc_nina", "account", {"owner": "nina", "bank": "WellsFargo", "balance": 12000.00})
env.add_node_with_attribute("acc_fraudnet", "account", {"owner": "fraudnet", "bank": "Citibank", "balance": 0.00})
env.add_node_with_attribute("acc_phishmaster", "account", {"owner": "phishmaster", "bank": "Chase", "balance": 0.00})

# Add accounts for legitimate organizations
env.add_node_with_attribute("acc_conedison", "account", {"owner": "ConEdison", "bank": "BankOfAmerica", "balance": 300000.00})
env.add_node_with_attribute("acc_tmobile", "account", {"owner": "TMobile", "bank": "Chase", "balance": 500000.00})
env.add_node_with_attribute("acc_bluediner", "account", {"owner": "BlueDiner", "bank": "FirstFinancial", "balance": 80000.00})
env.add_node_with_attribute("acc_wellesley", "account", {"owner": "WellesleyCollege", "bank": "BankOfAmerica", "balance": 1000000.00})

# Add ownership edges
env.add_ownership_edge("olivia", "acc_olivia")
env.add_ownership_edge("james", "acc_james")
env.add_ownership_edge("nina", "acc_nina")
env.add_ownership_edge("fraudnet", "acc_fraudnet")
env.add_ownership_edge("phishmaster", "acc_phishmaster")
env.add_ownership_edge("ConEdison", "acc_conedison")
env.add_ownership_edge("TMobile", "acc_tmobile")
env.add_ownership_edge("BlueDiner", "acc_bluediner")
env.add_ownership_edge("WellesleyCollege", "acc_wellesley")


planner = llmplanner.LLMPlanner(env)

data_len = 100
num_fraud_seq = 50

fraud_ind = random.sample(range(0, data_len), num_fraud_seq)

with open("sequences_json.json", "w") as f:
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



 
