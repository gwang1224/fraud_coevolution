import requests
import re
import json

with open("/Users/gracewang/Documents/fraud_coevolution/prompt.txt", 'r') as file:
    prompt = file.read()




def generate_transaction_seq(num_seq, env):
    """
    Generate fraud sequences based on prompt in prompt.txt

    Args:
        num_seq: number of sequences to be generated
        env: entities in the model environment (to check sequence validity)

    Returns:
        list of fraud sequences in json format
    """
    results = []

    action_pattern = r"Action\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(.+?)\s*\)"
    transaction_pattern = r"Transaction\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(\d+(?:\.\d{2})?)\s*\)"

    while len(results) < num_seq:
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'chevalblanc/gpt-4o-mini',
                    'prompt': prompt,
                    'stream': False
                }
            )
            res = response.json()['response']
            seq = json.loads(res).get('sequence', [])
        except Exception as e:
            print("Error parsing LLM response:", e)
            continue

        valid = True
        for step in seq:
            # Validate Action
            if step.startswith("Action("):
                match = re.fullmatch(action_pattern, step)
                # Both the 1st and 3rd group must be in env
                if not (match and match.group(1) in env and match.group(3) in env):
                    valid = False
                    print("Invalid Action step:", step)
                    break
            # Validate Transaction
            elif step.startswith("Transaction("):
                match = re.fullmatch(transaction_pattern, step)
                # Both the 1st and 3rd group must be in env
                if not (match and match.group(1) in env and match.group(3) in env):
                    valid = False
                    print("Invalid Transaction step:", step)
                    break
            else:
                valid = False
                print("Unrecognized step type:", step)
                break

        if valid:
            results.append(seq)

    return results


nodes = ['Olivia', 'Betty', 'ScamGov', 'ScamCo', 'BankOfAmerica', 'Chase', 'FirstFinancial', 'acc_olivia', 'acc_betty', 'acc_scamgov', 'Olivia_acc']

print(generate_transaction_seq(1, nodes))

                    
            


    
