import requests
import re
import json

class LLMPlanner():

    def __init__(self, env):
        self.env = env

    def write_prompt(self):
        """
        Generates prompt using input of entities from graph

        Args: 
            env: fraud env defined by fraud_env.py
        Returns:
            prompt as string
        """

        PROMPT_TEMPLATE = """
        YOUR TASK
        - Propose 1 valid action/transaction sequence within a network of entities and assets.
        - Follow these guidelines:


        GUIDELINES
        - An action must involve two entities (ENTITY1 and ENTITY2), action, channel, description.
        - ENTITY1 and ENTITY2 can be an individual or company.
        - ACTION is the action taken by ENTITY1 upon ENTITY2.
        - CHANNEL is the fraud mode (SMS, email, phone, etc).
        - DESCRIPTION is a detailed description of what action occurred (ex. for “impersonation” action, a potential description is “Posed as IRS agent”).
        - An Action must have **exactly five comma-separated fields** inside the parentheses:
        Action(ENTITY1, ACTION, ENTITY2, CHANNEL, DESCRIPTION)
        - A Transaction must have exactly four comma-separated fields:
        Transaction(ACCOUNT_FROM, FAST Payment, ACCOUNT_TO, AMOUNT)
        - Actions must be in chronological order.
        - For sequential actions, ENTITY2 in the first action should become ENTITY1 in the second action.
        - Money can only be fraudulently transferred if the account is compromised.
        - A fraudster can only transfer money into their bank account, however, once a victim’s account is compromised, a fraudster can transfer money from the victim’s account.
        - FAST transfers are instantaneous and irreversible.
        - A TRANSACTION should be at the end of the sequence.

        FRAUD ENVIRONMENT
        - YOU MUST USE THE EXACT ENTITY NAMES BELOW WITH THE SAME CAPITALIZATION. Do not invent or modify entity names.
        - If you want to reference someone's bank account, DO NOT say "Olivia's bank account", instead use the entities, such as "acc_olivia".

        - You may use:

        - {ind} as entities for victims.

        - {fraud} as entities for fraudsters.

        - {bank} as entities for banks.

        - {acc} as entities for accounts.


        EXAMPLE

        (This is an example of ONE complete sequence)
        Return a **single JSON dictionary** with the following structure, no verbose:

        {{
        "sequence": [
            "action(...)", 
            ...
            "transaction(...)"
        ]
        }}

        Do not include any text before or after the JSON. Return only the raw JSON dictionary.


        TASK
        - Be creative!
        - The entities should tell a story.
        - Choose diverse entities, action/transaction combinations and unique fraud techniques.
        - Use the following guidelines.
        - Include a variety of entities.
        - Experiment with different types of fraud (Identity theft, account takeover, SIM swap, but you are NOT limited to these!)

        - Do NOT include:
        - Explanations, comments, or notes.
        - Extra fields in Action or Transaction.
        - Non-matching entity names (use only names in the environment list).
        """

        i = ", ".join(self.env.get_individuals())
        f = ", ".join(self.env.get_fraudsters())
        b = ", ".join(self.env.get_banks())
        a = ", ".join(self.env.get_acc())

        return PROMPT_TEMPLATE.format(ind=i, fraud=f, bank=b, acc=a)
        

    def generate_sequence(self):
        """
        Generate fraud sequences based on prompt in prompt.txt

        Args:
            model: model name to use for generation
        Returns:
            response text (raw JSON string from model)
        """
        seq_prompt = self.write_prompt()
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': "llama3.2",
                    'prompt': seq_prompt,
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

## GEPA optimizer

# def main():
#     test = LLMPlanner()
#     response = test.generate_sequence()
#     print(response)


# if __name__ == "__main__":
#     main()