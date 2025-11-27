import requests
from collections import Counter

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

def explain_classification(seq: str) -> str:
    prompt = (
        "Explain why you classified this sequence as legit"
        f"Input:\n{seq}\n\nOutput:"
    )

    attempts = 0

    while True:
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
        return res
    
def ensemble_classify_sequence(seq:str) -> str:
    labels = [classify_sequence(seq) for _ in range(5)]

    winner, count = Counter(labels).most_common(1)[0]
    return winner, labels
        

def main():
    print(ensemble_classify_sequence("""['action(govco, phishing, james, email, sent fraudulent tax claim link)', 'action(james, clicked, govco, email, opened phishing link)', 'action(govco, gained_access, acc_james, link, obtained login credentials)', 'action(govco, transferred_funds, acc_james, bank, initiated fast payment to acc_govco)', 'transaction(acc_james, fast payment, acc_govco, 16000.0)'"""))
    print(explain_classification("""'action(govco, phishing, james, email, sent fraudulent tax claim link)', 'action(james, clicked, govco, email, opened phishing link)', 'action(govco, gained_access, acc_james, link, obtained login credentials)', 'action(govco, transferred_funds, acc_james, bank, initiated fast payment to acc_govco)', 'transaction(acc_james, fast payment, acc_govco, 16000.0)']"""))

if __name__ == "__main__":
    main()