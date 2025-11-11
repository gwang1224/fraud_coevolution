import requests
import json

def classify_sequence(seq: str):
    prompt = (
        "You are a strict classifier for financial sequences. A sequence contains actions and transactions.\n"
        "You must respond with **only one word**: either 'fraud' or 'legit'.\n"
        "Do not explain.\n\n"
        f"Input:\n{seq}\n\nOutput:"
    )

    while True:
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
        print(res)
        if res in ["fraud", "legit"]:
            return res