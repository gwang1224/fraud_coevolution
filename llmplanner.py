import requests
import re
import json


class LLMPlanner():
    
    def __init__(self):
        with open("/Users/gracewang/Documents/fraud_coevolution/prompt.txt", 'r') as file:
            self.prompt = file.read()
        self.env = ['olivia', 'betty', 'scamgov', 'scamco', 
                    'bankofamerica', 'chase', 'firstfinancial', 
                    'acc_olivia', 'acc_betty', 'acc_scamgov']
    
    def generate_sequence(self, model):
        """
        Generate fraud sequences based on prompt in prompt.txt

        Args:
            model: model name to use for generation

        Returns:
            response text (raw JSON string from model)
        """
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': self.prompt,
                    'stream': False
                }
            )
            #print("Generating seq")
            res =  response.json()['response'].lower()
            print(res)
        except Exception as e:
            print("Error parsing LLM response:", e)
            return None
        return res
    
    def validate(self, res):
        """
        Validates fraud patterns based on regex. Additionally enforces that
        the last step in the sequence must be a Transaction(...) step.
        """
        action_pattern = r"action\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(.+?)\s*\)"
        transaction_pattern = r"transaction\(\s*(.*?)\s*,\s*(.*?)\s*,\s*(.*?)\s*,\s*(\d+(?:\.\d{2})?)\s*\)"
action\(\s*(.*?)\s*,\s*(.*?)\s*,\s*(.*?)\s*,\s*(.*?)\s*,\s*(.*?)\s*\)$
        try:
            parsed = json.loads(res)
        except Exception as e:
            print("Invalid JSON format:", e)
            return False

        seq = parsed.get('sequence', [])
        # print(seq)

        valid = True

        for step in seq:
            # use lowercase when checking the prefix to be robust to case
            step_l = step.lower()
            if step_l.startswith("action("):
                match = re.fullmatch(action_pattern, step, re.IGNORECASE)
                if not (match and match.group(1).strip().lower() in self.env and match.group(3).strip().lower() in self.env):
                    valid = False
                    print("Invalid Action step:", step)
                    break
            elif step_l.startswith("transaction("):
                match = re.fullmatch(transaction_pattern, step, re.IGNORECASE)
                if not (match and match.group(1).strip().lower() in self.env and match.group(3).strip().lower() in self.env):
                    valid = False
                    print("Invalid Transaction step:", step)
                    break
            else:
                valid = False
                print("Unrecognized step type:", step)
                break

        # Enforce that the last step must be a Transaction(...)
        if valid:
            if not seq:
                print("Sequence is empty.")
                return False
            last_step = seq[-1]
            if not last_step.lower().startswith("transaction("):
                print("Last step is not a Transaction:", last_step)
                return False

        return valid
    

def main():
    test = LLMPlanner()
    model = "chevalblanc/gpt-4o-mini"
    response = test.generate_sequence(model)
    print(response)
    print(test.validate(response))

if __name__ == "__main__":
    main()
