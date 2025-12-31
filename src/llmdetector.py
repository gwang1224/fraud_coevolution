import requests
import json
from collections import Counter
import pandas as pd

class LLMDetector():
    """
    Detector that uses Ollama to classify fraudulent and legit 
    FAST-payment sequences.
    """

    def __init__(self, coev_file_path, model):
        self.coev_file_path = coev_file_path
        self.model = model
    
    def classify_sequence(self, seq: str, max_attempts=5) -> str:
        """
        Classifies one financial sequence in string format
        Given 5 attempts to generate single deterministic output "fraudulent" or "legit"

        Args:
            seq (str): financial sequence
        Returns:
            res: fraudulent or legit or None if sequence was unclassifiable
        """

        prompt = f"""
            You are a strict classifier for financial sequences. A sequence contains actions and transactions.
            You must respond: either 'fraud' or 'legit'.
            Do NOT explain why.

            Input:\n{seq}\n\nOutput:

            Your task is to determine whether a sequence of actions and transactions describes fraudulent behavior or legitimate behavior.
            You are NOT judging whether the data looks like a valid log, whether it is 'structured,' or whether it is 'a legitimate system input'.
            You are judging the content of the events themselves.

            Important Notes
            •	Do NOT classify based on format, structure, or appearance of a “system log.”
            •	Fraudulent keywords (e.g., phishing, fake, fraudulent link) indicate fraud, not legitimate monitoring activity.
            •	If both fraud and legitimate actions appear, classify based on the overall intent and outcome.
        """

        attempts = 0

        while True and attempts < max_attempts:
            attempts += 1
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        "temperature": 0
                    }
                }
            )
            res = response.json().get('response', '').strip().strip("'").lower()
            res = res.split()[0].strip(".,:;!?'\"")
            print(res)
            if res in ["fraud", "legit"]:
                return res
            
        return None
    

    def ensemble_classify_sequence(self, seq:str, num_calls:int=5) -> str:
        """
        Runs classify_sequence on financial sequence 5 times, gets "winner"
        Assess agreeableness between detection runs and whether model is stable
        """
        labels = [self.classify_sequence(seq) for _ in range(num_calls)]

        winner, count = Counter(labels).most_common(1)[0]
        stable = count/num_calls
        return winner, labels, stable


    def explain_classification(self, seq: str, result: str) -> str:
        """
        Prompts LLM to explain reasoning for classification
        Args:
            seq: financial sequence
            result: classification from ensemble_classify_sequence
        Returns:
            reason: explanation for classification
        """

        prompt = (
            f"Explain why you classified this sequence as {result}"
            f"Input:\n{seq}\n\nOutput:"
        )

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    "temperature": 0
                }
            }
        )
        res = response.json().get('response', '').strip().strip("'").lower()
        return res
    
    def run_detector(self):
        """
        Run detector on all sequences
        """
        error_seq = []
        res = []

        num_correct = 0
        false_pos = 0
        false_neg = 0
        total_seq = 0
        unclassifiable = 0

        with open(self.coev_file_path, "r") as f:
            data = json.load(f)
            print(data)

            for id in data:
                total_seq += 1

                print(f"Classifying Sequence {id}.")
                label = data[id]['label']
                sequence = data[id]['sequence']

                classification, __, stability = self.ensemble_classify_sequence(sequence)

                if classification == label:
                    num_correct += 1
                else:
                    if classification == "fraud" and label == "legit":
                        false_pos += 1
                    if classification == "legit" and label == "fraud":
                        false_neg += 1
                    else: 
                        unclassifiable += 1
                    error_seq.append({
                        'Sequence id': id,
                        'Sequence': sequence,
                        'Label': label,
                        'LLM Generated Label': classification,
                        'Stability': stability
                    })
            
            df_error = pd.DataFrame(error_seq)
            print(df_error)
            df_error.to_csv("data/detector/v2/detector_errors_v2_4.csv")

        res.append({
            'Accuracy': num_correct/total_seq,
            'False positive': false_pos/total_seq,
            'False negative': false_neg/total_seq,
            'Unclassifiable': unclassifiable/total_seq
        })
        df_res = pd.DataFrame(res)
        print(df_res)
        df_res.to_csv("data/detector/v2/detector_res_v2_4.csv")
            

detector = LLMDetector("data/coev/coev_seq_v2.json", "llama3.2")
detector.run_detector()