import requests
import json

def classify_sequence(seq: str, max_attempts=10) -> str:
    prompt = (
        "You are a strict classifier for financial sequences. A sequence contains actions and transactions.\n"
        "You must respond with **only one word**: either 'fraud' or 'legit'.\n"
        "Do not explain.\n\n"
        f"Input:\n{seq}\n\nOutput:"
    )

    attempts = 0

    while True and attempts < max_attempts:
        attempts += 1
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False,
                'options': {
                    "temperature": 0
                }
            }
        )
        res = response.json().get('response', '').strip().strip("'").lower()
        if res in ["fraud", "legit"]:
            return res
        
    return None
    
        

def main():
    print(classify_sequence(""""action(fishmaster, phishing, sally, email, sent fraudulent bank login link)",
      "action(sally, clicked, fishmaster, email, opened malicious link)",
      "action(sally, entered_credentials, fishmaster, unknown, provided account credentials)",
      "action(fishmaster, accessed_account, acc_sally, unknown, fraudster gained access to account)",
      "transaction(acc_sally, fast payment, acc_fishmaster, 4800.0)"
"""))

if __name__ == "__main__":
    main()