import requests
import re
import json

class LLMPlanner():

    def __init__(self):
        with open("/Users/gracewang/Documents/fraud_coevolution/prompts/prompt2.txt", 'r') as file:
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


    

def main():
    test = LLMPlanner()
    model = "llama3.2"
    response = test.generate_sequence(model)
    print(response)


if __name__ == "__main__":
    main()