import fraud_env
import llmplanner
import pydantic_validator as eval

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


# Generate fraud sequence
planner = llmplanner.LLMPlanner(env)
seq = planner.generate_sequence()
print(seq)

# Validate sequence
try:
    T = eval.SequenceModel.model_validate(seq, context={"entities": env.get_nodes()})
    print("✅ Validation passed")
except Exception as e:
    print("❌ Validation failed:", e)




