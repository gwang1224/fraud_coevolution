import requests
import re
import json
import fraud_env
import pydantic_validator as pv


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
        - You must use the exact entity names. Do not invent or modify entity names.

        - You may use:

        - {ind} as entities for victims.

        - {fraud} as entities for fraudsters.

        - {bank} as entities for banks.

        - {acc} as entities for accounts.


        EXAMPLE
        (This is an example of ONE complete sequence)
        Take inspiration from this, do NOT copy it, be original
        {{
        "sequence": [
            "action(<entity1>, Impersonation, <entity2>, Call, Posed as IRS agent)",
            "action(<entity2>, Sensitive Info Submission, <entity1>, SMS, sent SSN + DOB)",
            "action(<entity1>, Social engineering, <bank1>, Call, ...)",
            "transaction(<entity2 bank account>, FAST Payment, <entity1 bank account>, 3000.00)"
        ]
        }}

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

        EXAMPLE 1:
        {{
        "sequence": [
            "action(Olivia, payment, BankOfAmerica, app, paid electricity bill)",
            "transaction(acc_olivia, fast payment, acc_utility, 200.00)"
        ]
        }}

        EXAMPLE 2:
        {{
        "sequence": [
            "action(Olivia, payment, Grace, mobile phone, payment to friend)",
            "transaction(acc_olivia, fast payment, acc_grace, 200.00)"
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
        def extract_balanced_json(text):
            start = text.find('{')
            if start == -1:
                return None

            open_braces = 0
            open_brackets = 0
            for i in range(start, len(text)):
                if text[i] == '{':
                    open_braces += 1
                elif text[i] == '}':
                    open_braces -= 1
                elif text[i] == '[':
                    open_brackets += 1
                elif text[i] == ']':
                    open_brackets -= 1

                if open_braces == 0 and open_brackets == 0 and i > start:
                    candidate = text[start:i+1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        continue

            return None

        base_prompt = self.fraud_prompt() if type == 'fraud' else self.legit_prompt()
        current_prompt = base_prompt
        valid_sequence = False
        attempt_count = 0

        while not valid_sequence:
            attempt_count += 1
            print("\n" + str(attempt_count))
            print(current_prompt)
            try:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': "llama3.2",
                        'prompt': current_prompt,
                        'stream': False
                    }
                )
                raw = response.json().get('response', '').strip()
                if not raw:
                    print("Empty LLM response.")
                    current_prompt += "\nNOTE: Last response was empty. Try again and ensure to respond with JSON only.\n"
                    continue

                json_text = extract_balanced_json(raw)
                if not json_text:
                    print("No valid or complete JSON found.")
                    print("Raw output:", raw)
                    current_prompt += f"\nNOTE: Last output had no valid JSON. Only output a clean JSON dictionary.\nRaw output: {raw}\n"
                    continue

                try:
                    res = json.loads(json_text.lower())
                except json.JSONDecodeError as e:
                    print("Error parsing extracted JSON:", e)
                    current_prompt += f"\nNOTE: JSON error occurred: {str(e)}\nInvalid JSON was: {json_text}\n"
                    continue

                if not self.syntax_validator(res):
                    current_prompt += f"\nNOTE: Your sequence failed syntax validation. Please revise to follow the action and transaction format exactly.\nSequence: {res}\n"
                    continue

                reasoning = self.semantic_validator(res)
                if reasoning:
                    current_prompt += f"\nNOTE: Semantic validation failed. Review this reasoning and try again.\n{reasoning}\n"
                    continue

                valid_sequence = True
                return res, attempt_count

            except Exception as e:
                print("❌ Unexpected error:", e)
                current_prompt += f"\nNOTE: An unexpected error occurred while processing your sequence: {str(e)}\n"
    


## GEPA optimizer
    ## GEPA style optimizer
    def semantic_validator(self, prompt):

        validator_prompt = f"""
        You are a fraud simulation environment validator. Your job is to determine whether a given sequence of actions and transactions is *logically valid*, based on realistic financial behavior and common sense.

        Here is the input sequence:
        {prompt}

        Rules to follow:
        1. Only participants (individuals or fraudsters) can perform actions.
        2. Accounts and banks cannot perform actions directly.
        3. SIM swaps must be done by a person (not an account), and must target a telco.
        4. Transactions must not be initiated by fraudsters directly.
        5. The sequence must make sense as a story — cause and effect should be coherent.

        Instructions:
        - On the first line, output exactly one word: "valid" or "invalid".
        - On the following lines, provide a clear explanation of your reasoning.
        - If invalid, explain why and suggest how to fix it.
        - Use the following format strictly for parsing:
        
        <valid or invalid>
        Reasoning:
        <your detailed explanation here>
        """

        response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",  # Or your fine-tuned validator model
            "prompt": validator_prompt,
            "stream": False,
            "options": {"temperature": 0}
        }
    )
        label = response.json().get("response", "").strip().lower()
        if label.startswith('valid'):
            return None
        else:
            NEW_PROMPT = f"Here is the sequence you generated and why it's invalid: {prompt}"
            return NEW_PROMPT + label

    def syntax_validator(self, prompt):
        try:
            T = pv.SequenceModel.model_validate(prompt, context={"entities": self.env.get_nodes()})
            return True
        except Exception as e:
            print("❌ Validation failed:", e)
            return False

def main():

    env = fraud_env.FraudEnv()

    env.add_node_with_attribute("bankofamerica", "bank")
    env.add_node_with_attribute("chase", "bank")
    env.add_node_with_attribute("firstfinancial", "bank")

    env.add_node_with_attribute("sally", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_sally", "account", {"owner": "sally", "bank": "bankofamerica", "balance": 6000.00})
    env.add_node_with_attribute("grace", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_grace", "account", {"owner": "grace", "bank": "chase", "balance": 400000.00})
    env.add_node_with_attribute("bill", "participant", {"role": "individual", "isFraudster": False})
    env.add_node_with_attribute("acc_bill", "account", {"owner": "bill", "bank": "firstfinancial", "balance": 15000.00})

    env.add_node_with_attribute("ConEdison", "participant", {"role": "utility", "isFraudster": False})
    env.add_node_with_attribute("acc_conedison", "account", {"owner": "ConEdison", "bank": "bankofamerica", "balance": 300000.00})
    env.add_node_with_attribute("TMobile", "participant", {"role": "telecom", "isFraudster": False})
    env.add_node_with_attribute("acc_tmobile", "account", {"owner": "TMobile", "bank": "chase", "balance": 500000.00})
    
    env.add_node_with_attribute("govco", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_govco", "account", {"owner": "govco", "bank": "citibank", "balance": 0.00})
    env.add_node_with_attribute("insuranceco", "participant", {"role": "fraudster", "isFraudster": True})
    env.add_node_with_attribute("acc_insuranceco", "account", {"owner": "insuranceco", "bank": "bankofamerica", "balance": 0.00})
    env.add_node_with_attribute("insurancenet", "participant", {"role": "fraudster", "isFraudster": True})

    # Generate fraud sequence
    planner = LLMPlanner(env)
    # print(planner.generate_sequence("legit"))
    print(planner.generate_sequence("fraud"))
    # print(planner.syntax_validator(sequence))



if __name__ == "__main__":
    main()