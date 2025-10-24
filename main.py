import fraud_env
import llmplanner
import eval

env = fraud_env.FraudEnv()

# Add banks
env.add_node_with_attribute("BankOfAmerica", "bank")
env.add_node_with_attribute("Chase", "bank")
env.add_node_with_attribute("FirstFinancial", "bank")

# Add individuals
env.add_node_with_attribute("Olivia", "individual", {"role": "victim"})
env.add_node_with_attribute("Betty", "individual", {"role": "victim"})

# Add fraudsters
env.add_node_with_attribute("ScamGov", "fraudster", {"role": "fraudco", "status": "active", "description": "Impersonates gov for SID"})
env.add_node_with_attribute("ScamCo", "fraudster", {"role": "fraudco", "status": "active", "description": "Impersonates gov for SID"})

# Add accounts (using valid banks)
env.add_node_with_attribute("acc_olivia", "account", {"owner": "Olivia", "bank": "BankOfAmerica", "balance": 60000.00})
env.add_node_with_attribute("acc_betty", "account", {"owner": "Betty", "bank": "Chase", "balance": 4000.00})
env.add_node_with_attribute("acc_scamgov", "account", {"owner": "ScamGov", "bank": "FirstFinancial", "balance": 0.00})

# Add ownership edges
env.add_ownership_edge("Olivia", "acc_olivia")
env.add_ownership_edge("Betty", "acc_betty")
env.add_ownership_edge("ScamGov", "acc_scamgov")


# Generate fraud sequence
planner = llmplanner.LLMPlanner()
seq = planner.generate_sequence()
print(seq)

# Validate sequence

eval.


