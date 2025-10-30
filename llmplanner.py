import requests
import re
import json
import fraud_env


class LLMPlanner():

    def __init__(self, env):
        self.env = env

    def fraud_prompt(self):
        """
        Generates fraudulent prompt using input of entities from graph

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
        Take inspiration from this, do NOT copy it, be original
        {{"sequence": [
            "action(ScamGov, Impersonation, Olivia, Call, Posed as IRS agent)",
            "action(Olivia, Sensitive Info Submission, ScamGov, SMS, sent SSN + DOB)",
            "action(ScamGov, Social engineering, BankOfAmerica, Call, ...)",
            "transaction(acc_olivia, FAST Payment, acc_scamgov, 3000.00)"
        ]}}

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
    
    def legit_prompt(self):
        """
        Generates fraudulent prompt using input of entities from graph

        Args: 
            env: fraud env defined by fraud_env.py
        Returns:
            prompt as string
        """
        PROMPT_TEMPLATE = """
        YOUR TASK  
        - Propose 1 valid **legitimate** action/transaction sequence within a network of entities and assets.  
        - Follow these guidelines:

        GUIDELINES  
        - An action must involve two entities (ENTITY1 and ENTITY2), action, channel, description.  
        - ENTITY1 and ENTITY2 can be an individual or company.  
        - ACTION is the action taken by ENTITY1 upon ENTITY2.  
        - CHANNEL is the communication or transaction method (e.g., SMS, email, phone, online platform, etc.).  
        - DESCRIPTION is a detailed explanation of the legitimate interaction (e.g., for “account verification” action, a potential description is “confirmed identity through OTP”).  
        - An Action must have **exactly five comma-separated fields** inside the parentheses:  
        `Action(ENTITY1, ACTION, ENTITY2, CHANNEL, DESCRIPTION)`  
        - A Transaction must have exactly four comma-separated fields:  
        `Transaction(ACCOUNT_FROM, FAST Payment, ACCOUNT_TO, AMOUNT)`  
        - Actions must be in chronological order.  
        - For sequential actions, ENTITY2 in the first action should become ENTITY1 in the second action.  
        - Money can only be transferred between **authorized users or businesses** for **legitimate reasons**.  
        - FAST transfers should reflect real, lawful payments between trusted parties.  
        - A TRANSACTION should be at the end of the sequence.

        FRAUD ENVIRONMENT  
        - YOU MUST USE THE EXACT ENTITY NAMES BELOW WITH THE SAME CAPITALIZATION. Do not invent or modify entity names.  
        - If you want to reference someone's bank account, DO NOT say "Olivia's bank account", instead use the entities, such as "acc_olivia".

        - You may use:  
        - {ind} as entities for individuals.  
        - {bank} as entities for banks.  
        - {acc} as entities for accounts.

        EXAMPLE:
        {{
        "sequence": [
            "action(Olivia, payment, BankOfAmerica, app, paid electricity bill)",
            "transaction(acc_olivia, fast payment, acc_utility, 200.00)"
        ]
        }}

        (This is an example of ONE complete sequence)  
        Return a **single JSON dictionary** with the following structure, no verbose:  

        ```json
        {{
        "sequence": [
            "action(...)",
            ...
            "transaction(...)"
        ]
        }}

        IMPORTANT
        - All actions must make logical, real-world sense. Avoid circular transactions or repeated actors receiving and sending money for unclear reasons.
        - The purpose of each action should be contextually valid (e.g., utility payments, rent transfers, tuition).
        - A payment must only occur once the recipient has provided value (e.g., consultation, service, product).
        - Do NOT include fraudsters in legitimate sequences.
        """
        i = ", ".join(self.env.get_individuals())
        b = ", ".join(self.env.get_banks())
        a = ", ".join(self.env.get_acc())

        return PROMPT_TEMPLATE.format(ind=i, bank=b, acc=a)


        

    def generate_sequence(self, type):
        """
        Generate fraud sequences based on prompt in prompt.txt

        Args:
            model: model name to use for generation
        Returns:
            response text (raw JSON string from model)
        """

        # Brace parser
        def extract_balanced_json(text):
            start = text.find('{')
            if start == -1:
                return None
            open_braces = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    open_braces += 1
                elif text[i] == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        return text[start:i+1]
            return None  # unbalanced

        if type == 'fraud':
            p = self.fraud_prompt()
        if type == 'legit':
            p = self.legit_prompt()
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': "llama3.2",
                    'prompt': p,
                    'stream': False
                }
            )
            try:
                raw = response.json().get('response', '').strip()
                if not raw:
                    print("Empty LLM response.")
                    return None

                # Extract the first JSON block if extra data exists
                json_text = extract_balanced_json(raw)
                if not json_text:
                    print("No valid or complete JSON found.")
                    print("Raw output:", raw)
                    return None
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

def main():

    env = fraud_env.FraudEnv()

    # Add banks
    env.add_node_with_attribute("BankOfAmerica", "bank")
    env.add_node_with_attribute("bankofamerica", "bank")
    env.add_node_with_attribute("chase", "bank")
    env.add_node_with_attribute("firstfinancial", "bank")

    # Add individuals
    env.add_node_with_attribute("sally", "individual")
    env.add_node_with_attribute("grace", "individual")
    env.add_node_with_attribute("bill", "individual")

    # Add fraudsters
    env.add_node_with_attribute("scamgov", "fraudster", {"status": "active", "description": "Impersonates gov for SID"})
    env.add_node_with_attribute("scamco", "fraudster", {"status": "active", "description": "Impersonates gov for SID"})

    # Add accounts (using valid banks)
    env.add_node_with_attribute("acc_sally", "account", {"owner": "sally", "bank": "BankOfAmerica", "balance": 6000.00})
    env.add_node_with_attribute("acc_grace", "account", {"owner": "grace", "bank": "Chase", "balance": 400000.00})
    env.add_node_with_attribute("acc_scamgov", "account", {"owner": "scamgov", "bank": "FirstFinancial", "balance": 0.00})

    # Add ownership edges
    env.add_ownership_edge("sally", "acc_sally")
    env.add_ownership_edge("grace", "acc_grace")
    env.add_ownership_edge("scamgov", "acc_scamgov")


    # Generate fraud sequence
    planner = LLMPlanner(env)
    print(planner.generate_sequence("legit"))
    print(planner.generate_sequence("fraud"))


if __name__ == "__main__":
    main()