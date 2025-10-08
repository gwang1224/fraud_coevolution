import requests
import re
import json

class LLMPlanner():

    def __init__(self):
        with open("/Users/gracewang/Documents/fraud_coevolution/prompt.txt", 'r') as file:
            self.prompt = file.read()
        self.env = ['olivia', 'betty', 'scamgov', 'scamco', 
                    'bankofamerica', 'chase', 'firstfinancial', 
                    'acc_olivia', 'acc_betty', 'acc_scamgov', 'acc_scamco']
        
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
            try:
                raw = response.json().get('response', '').strip()
                if not raw:
                    print("Empty LLM response.")
                    return None

                # Extract the first JSON block if extra data exists
                import re
                match = re.search(r'\{[\s\S]*?\}', raw)
                if not match:
                    print("No valid JSON found in LLM output.")
                    print("Raw output:", raw)
                    return None

                json_text = match.group(0).strip()
                try:
                    res = json.loads(json_text.lower())
                except json.JSONDecodeError as e:
                    print("Error parsing extracted JSON:", e)
                    print("Raw JSON text:\n", json_text)
                    return None
            except Exception as e:
                print("Error parsing LLM response:", e)
                return None
        except Exception as e:
            print("Error parsing LLM response:", e)
            return None
        return res
    
    def validate(self, output):
        """
        Validates fraud patterns based on regex.
        Criteria:
            - matches action and transaction regex sequences
            - last sequence should be a transaction seq

        Return:
            valid- whether or not the seqence is valid
            rof- reason of failure
                type: type of input
                action: error with action sequence
                transaction: error with transaction sequence
                end: end seq is not transaction

        """
        if not output or not isinstance(output, dict):
            print("input is not a dictionary: not valid")
            return False, "type"
        valid = True
        rof = None

        action_pat = r"^action\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*\)$"
        transact_pat = r"transaction\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(\d+(?:\.\d{2})?)\s*\)"

        # Validates input as dict
        if not isinstance(output, dict):
            print("input is not a dictionary: not valid")
            rof = "type"
            valid = False

        # Validates 'sequence' exists and is a list
        try:
            seqs = output.get('sequence')
            if not isinstance(seqs, list):
                raise AttributeError
        except AttributeError:
            print("sequence is not a list: not valid")
            rof = "type"
            return False
        
        for seq in seqs:
            # Checks action step
            if seq.startswith("action("):
                match = re.fullmatch(action_pat, seq)
                if not (match and match.group(1).strip() in self.env and match.group(3).strip() in self.env):
                    valid = False
                    rof = "action"
                    print("Invalid action step: ", seq)
                    break
            if seq.startswith("transaction("):
                match = re.fullmatch(transact_pat, seq)
                if not (match and match.group(1).strip() in self.env and match.group(3).strip() in self.env):
                    valid = False
                    rof = "transaction"
                    print("Invalid transaction step: ", seq)
                    break

        # Enforces that last step must be transaction step
        # Last step should indicate money was fraudulently transfered
        if valid:
            last_step = seqs[-1]
            if not last_step.startswith("transaction("):
                rof = "end"
                print("Last step is not a transaction: ", last_step)
                valid = False
            
        return valid, rof



    

def main():
    # --------------- Testing ------------------
    test = LLMPlanner()
    model = "chevalblanc/gpt-4o-mini"
    response = test.generate_sequence(model)
    print(response)
    print(type(response))
    valid, reason = test.validate(response)
    print(valid, reason)

    # --------------- Testing validate ------------------
    # Shouldn't work
    ex1 = """
    {
    "sequence_id": "1",
    "sequence": [
        "action(scamco, phishing email, olivia, email, scamco urgent: verify your account)",
        "action(olivia, sensitive info submission, scamco, click, clicked on link to verify account)",
        "action(scamco, social engineering, scamgov, call, ...)",
        "action(olivia, sensitive info submission, scamgov, phone, sent ssn + dob)",
        "action(scamco, account takeover, olivia, call, scammed olivia out of login details)",
        "transaction(scamco, money transfer, olivia's bankaccount (acc_olivia), 5000.00)"
    ]}
    """
    seq1 = json.loads(ex1)
    # print(seq1)

    ex2 = """
    {
    "sequence_id": "1",
    "sequence": [
        "action(scamco, phishing email, olivia, email, scamco urgent: verify your account)",
        "action(olivia, sensitive info submission, scamco, click, clicked on link to verify account)",
        "action(scamco, social engineering, scamgov, call, ...)",
        "action(olivia, sensitive info submission, scamgov, phone, sent ssn + dob)",
        "action(scamco, account takeover, olivia, call, scammed olivia out of login details)",
        "transaction(scamco, money transfer, acc_olivia, 500.00)"
    ]}
    """
    seq2 = json.loads(ex2)
    # print(seq2)

    # print(test.validate(seq1))
    # print(test.validate(seq2))





if __name__ == "__main__":
    main()