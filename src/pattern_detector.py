import json
import requests

def generate_pattern(file, max_patterns) -> str:
    with open(file, 'r') as f:
        data = json.load(f)
        formatted_fraud = {key: value for key, value in data.items() if value.get("label") == "fraud"}
        formatted_legit = {key: value for key, value in data.items() if value.get("label") == "legit"}

        
    TEMPLATE = """
    YOUR TASK

    Identify {max_patterns} distinct, high-level behavioral patterns that occur in fraudulent sequences and do NOT occur in legitimate sequences.

    These patterns should describe general strategies, tactics, or behavioral structures—not specific entities or specific wording from examples.

    Fraudulent sequences:
    {fraud_seqs}

    Legitimate sequences:
    {legit_seqs}

    You must:
	•	Extract generalizable fraud patterns (e.g., “phishing to obtain credentials,” “account takeover followed by unauthorized transfer,” “social engineering leading to information disclosure”).
	•	Ensure none of the patterns are present in legitimate sequences.
	•	Avoid sequence-specific details.
	•	Ensure each pattern describes behavior, not a literal line from the dataset.


    Format:
    Return the identified patterns in a semicolon-separated file (similar to a CSV) as shown in the example,
    with pattern_number and pattern_name columns:
    semicolon-separated file
    pattern_number;pattern_name
    1;pattern 1
    2;pattern 2
    3;pattern 3
    Only return the semicolon-separated list, no comments or explanation needed.
    """

    prompt = TEMPLATE.format(fraud_seqs=formatted_fraud, legit_seqs=formatted_legit, max_patterns=max_patterns)

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'llama3.2',
            'prompt': prompt,
            'stream': False
        }
    )
    return response.json().get('response', '')

        

print(generate_pattern("data/coev/coev_seq_v2.json", 5))
        