import requests
import re
import json
import fraud_env
import pydantic_syntax as pv


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

    def generate_sequence(self, prompt):
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': "llama3.2",
                'prompt': prompt,
                'stream': False
            }
        )
        raw = response.json().get('response', '').strip()
        return raw
    
    def generate_valid_fraud_seq(self):

        prompt = self.fraud_prompt()

        while True:
            sequence = self.generate_sequence(prompt)
            print(sequence)

            # Try to parse JSON
            try:
                seq_as_dict = json.loads(sequence)
            except Exception as e:
                # Append feedback to prompt and retry
                prompt += f"\nThe previous output was not valid JSON. Checking for missing trailing ] or }} Error: {e}\n"
                continue

            # Syntax check
            syntax_res = self.syntax_validator(seq_as_dict)
            if syntax_res is True:
                return seq_as_dict
            else:
                # Append syntax error message to prompt and retry
                prompt += f"\nYour previous sequence failed syntax validation: {syntax_res}\n"
                continue
        return sequence
            

    
## GEPA optimizer
    ## GEPA style optimizer
    def semantic_validator(self, sequence):

        validator_prompt = """
        You are a fraud simulation environment validator. Your job is to determine whether a given sequence of actions and transactions is *logically valid*, based on realistic financial behavior and common sense.

        Here is the input sequence:
        {sequence}

        Rules to follow:
        1. Only participants (individuals or fraudsters) can perform actions (ENTITY1). Fraudsters are participants and can perform actions.
        2. Accounts and banks cannot *initiate* actions — they must NEVER appear as ENTITY1 — but they can appear as ENTITY2 (e.g., fraudsters calling a bank).
        3. SIM swaps must be done by a participant (not an account) and must target a telecom.
        4. The sequence must make sense as a story — cause and effect should be coherent.

        Here is the format of the action/transaction sequences:
        - An Action must have **exactly five comma-separated fields** inside the parentheses:
        Action(ENTITY1, ACTION TAKEN BY ENTITY1 UPON ENTITY2, ENTITY2, CHANNEL, DESCRIPTION)
        - A Transaction must have exactly four comma-separated fields:
        Transaction(ACCOUNT_FROM, FAST Payment, ACCOUNT_TO, AMOUNT)

        NOTE: Banks and accounts can only be ENTITY2, never ENTITY1. It is valid for a fraudster or individual to *target* a bank or account in an action — for example, a fraudster social engineering bankofamerica is valid.

        Here are the entity labels:
        - {ind} as entities for victims.
        - {fraud} as entities for fraudsters (fraudsters are participants and CAN initiate actions; for example, govco is a fraudster and CAN perform actions).
        - {bank} as entities for banks.
        - {acc} as entities for accounts.

        Instructions:
        - On the first line, output exactly one word: "valid" or "invalid".
        - On the following lines, provide a clear explanation of your reasoning.
        - If invalid, explain why and suggest how to fix it.
        - Use the following format strictly for parsing:
        
        <valid or invalid>
        Reasoning:
        <your detailed explanation here>

        NOTE: Fraudsters such as {fraud} ARE allowed to perform actions. For example, govco is a fraudster and CAN initiate actions.
        """

        i = ", ".join(self.env.get_individuals())
        f = ", ".join(self.env.get_fraudsters())
        b = ", ".join(self.env.get_banks())
        a = ", ".join(self.env.get_acc())

        validator_prompt = validator_prompt.format(sequence=sequence, ind=i, fraud=f, bank=b, acc=a)


        response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "chevalblanc/gpt-4o-mini", 
            "prompt": validator_prompt,
            "stream": False,
            "options": {"temperature": 0}
        }
    )
        label = response.json().get("response", "").strip().lower()
        if label.startswith('valid'):
            return None
        else:
            NEW_PROMPT = f"Here is the sequence you generated and why it's invalid: {sequence}"
            return NEW_PROMPT + label

    def syntax_validator(self, sequence):
        try:
            T = pv.SequenceModel.model_validate(sequence, context={"entities": self.env.get_nodes()})
            return True
        except Exception as e:
            print("❌ Validation failed:", e)
            return e

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

    #---------------------------TESTING-------------------------------
    ## Semantic Validator

    ## Expected: NOT VALIDATED -> return new prompt
#     print("\nExpected False: ")
#     print(planner.syntax_validator(
# {"sequence": [
#             "action(govco, sally, Call, Posed as IRS agent)",
#             "action(sally, Sensitive Info Submission, govco, SMS, sent SSN + DOB)",
#             "action(govco, Social engineering, bankofamerica, ..., ...)",
#             "transaction(acc_sally, FAST Payment, acc_govco, 3000.00)"
#         ]}))

#     ## Expected: VALIDATED -> return None
#     print("\nExpected True: ")
#     print(planner.syntax_validator(
# {"sequence": [
#             "action(govco, Impersonation, sally, Call, Posed as IRS agent)",
#             "action(sally, Sensitive Info Submission, govco, SMS, sent SSN + DOB)",
#             "action(govco, Social engineering, bankofamerica, ..., ...)",
#             "transaction(acc_sally, FAST Payment, acc_govco, 3000.00)"
#         ]}
#     ))

    print(planner.generate_valid_fraud_seq())


if __name__ == "__main__":
    main()