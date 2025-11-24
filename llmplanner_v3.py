import requests
import re
import json
import fraud_env
import pydantic_validator as pv
from json_repair import repair_json
import random



class LLMPlanner():

    def __init__(self, env):
        self.env = env
        self.pv = pv.UniversalRulesValidator(self.build_entity_registry())

    def select_characters(self) -> dict:

        # Random victim
        victim = random.choice(self.env.get_individuals())
        victim_acc = next((n for n, d in self.env.G.nodes(data=True) if d.get("owner") == victim), None)
        bank = self.env.G.nodes[victim_acc]['bank']
        
        # Random fraudster
        fraudster = random.choice(self.env.get_fraudsters())
        fraudster_acc = next((n for n, d in self.env.G.nodes(data=True) if d.get("owner") == fraudster), None)

        # Assume fraudster is taking 0.8 of balance
        transfer_amount = self.env.G.nodes[victim_acc]["balance"] * 0.8

        return {"victim": victim, "victim account": victim_acc, "bank": bank, "fraudster": fraudster, "fraudster account": fraudster_acc, "transfer amount": transfer_amount}
        
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

        - Propose ONE valid fraud sequence.
        - Use ONLY the provided entities and transfer amounts.

        You must construct a coherent story using **exactly one victim and one fraudster**, following chronological logic.

        Use ONLY THESE entities in actions and the final transaction. Do not invent new entities.
        - Victim: {victim}
        - Victim Account: {victim_acc}
        - Fraudster: {fraudster}
        - Fraudster Account: {fraudster_acc}
        - Transfer Amount: {transfer_amount}

        
        Format rules:
        ACTION FORMAT (exactly 5 comma-separated fields):
            action(ENTITY1, ACTION, ENTITY2, CHANNEL, DESCRIPTION)
        
        TRANSACTION FORMAT (exactly 4 comma-separated fields):
            transaction(ACCOUNT_FROM, FAST Payment, ACCOUNT_TO, AMOUNT)

        GUIDELINES
        - ENTITY1 must be a participant (victim or fraudster), NOT a bank or account.
        - ENTITY2 can be a bank, participant, or account.
        - CHANNEL is the fraud mode (exmples are not limited to SMS, email, phone, etc).
        - DESCRIPTION is a  description of what action occurred (ex. for “impersonation” action, a potential description is “Posed as IRS agent”).
        - Actions must flow logically (cause → effect → compromise → money stolen).
        - The **final step MUST be the transaction**.
        - Be creative


       Example structure (do not copy content):
        {{
        "sequence": [
            "action({fraudster}, <action>, {victim}, <channel>, Posed as tax officer)",
            "action({victim}, <action>, {fraudster}, <channel>, sent SSN and credentials)",
            "action({fraudster}, <action>, {victim_acc}, <channel>, gained full access)",
            "transaction({victim_acc}, FAST Payment, {fraudster_acc}, {transfer_amount})"
        ]
        }}

        DO NOT INCLUDE:
        - Any additional entities besides those provided.
        - More than one fraudster or victim.
        - Any text before or after the JSON.
        - Explanations, comments, bullet points.

        Return ONLY a JSON dictionary in the following format:
        {{
        "sequence": [
            "action(...)",
            ...,
            "transaction(...)"
        ]
        }}
        """

        characters = self.select_characters()

        v = characters['victim']
        v_acc = characters['victim account']
        f = characters['fraudster']
        f_acc = characters['fraudster account']
        amount = characters['transfer amount']

        return PROMPT_TEMPLATE.format(victim = v, victim_acc = v_acc, fraudster = f, fraudster_acc = f_acc, transfer_amount = amount)
    
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

    def call_model(self, prompt):
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': "mistral",
                'prompt': prompt,
                'stream': False
            }
        )
        raw = response.json().get('response', '').strip()
        return raw
            
    def build_entity_registry(self):
        ROLE_TO_ENTITYTYPE = {
            "individual": pv.EntityType.INDIVIDUAL,
            "fraudster": pv.EntityType.FRAUDSTER,
            "bank": pv.EntityType.BANK,
            "account": pv.EntityType.ACCOUNT,
            "telecom": pv.EntityType.TELECOM,
            "utility": pv.EntityType.ORGANIZATION,
            "restaurant": pv.EntityType.ORGANIZATION,
            "institution": pv.EntityType.ORGANIZATION,
        }
        registry = {}

        for node, attrs in self.env.G.nodes(data=True):

            role = attrs.get("role")
            etype = ROLE_TO_ENTITYTYPE.get(role)

            registry[node] = pv.Entity(name=node, type=etype)

        return registry
    
    def generate_valid_fraud_seq(self, max_attempts=15):
        """
        Generates a valid fraud sequence through GEPA-stype prompting the LLM
        until both syntax and semantics are validated
        """

        prompt = self.fraud_prompt()
        attempts = 0
        valid_seq = False

        num_syntax_errors = 0
        num_semantic_errors = 0

        while not valid_seq and attempts < max_attempts:
            print(f"\n\n\n{prompt}")
            attempts += 1
            raw = self.call_model(prompt)

            # Stage 1: Validate JSON format
            json_text = raw[raw.find("{"):]
            json_text = repair_json(json_text).lower()

            try:
                sequence = json.loads(json_text)
            except Exception as e:
                error_msg = (
                    f"\nThe JSON you produced was invalid and could not be parsed.\n"
                    f"Error: {type(e).__name__}: {str(e)}\n"
                    f"Here is the exact output you produced:\n{json_text}\n\n"
                    "Fix the JSON formatting and return ONLY valid JSON."
                )
                num_syntax_errors += 1
                print(error_msg)

                prompt += error_msg
                continue

            if "sequence" not in sequence:
                prompt += "\n Error. The JSON you produced did not contain 'sequence' key."
                num_syntax_errors += 1
                continue

            # Detect broken / multiline / incomplete steps
            broken = any(
                not isinstance(step, str) or "(" not in step or ")" not in step
                for step in sequence["sequence"]
            )

            if broken:
                num_syntax_errors += 1
                err_block = (
                    "\nYour previous output was invalid because at least one action or transaction "
                    "was split across multiple lines or is missing parentheses.\n"
                    "Each step MUST be exactly one line of the form:\n"
                    "action(...)\n"
                    "transaction(...)\n"
                    "Here is what you returned:\n"
                    f"{json.dumps(sequence, indent=2)}\n"
                    "Regenerate a NEW JSON dictionary following the rules."
                )
                print(err_block)
                prompt += err_block
                continue

            # Check if 'sequence' is present
            if 'sequence' not in sequence:
                num_syntax_errors += 1
                error_msg = (
                    "\nYour JSON did not include a valid 'sequence' list.\n"
                    f"You returned:\n{json_text}\n"
                    "Return ONLY: {\"sequence\": [ ... ]}"
                )
                print(error_msg)
                prompt += error_msg
                continue

            # Stage 2: SYNTAX CHECK
            syntax_ok, syntax_errors = self.pv.validate_syntax(sequence['sequence'])
            print("Syntax OK:", syntax_ok)

            if not syntax_ok:
                num_syntax_errors += 1
                err_block = (
                    "\nYour previous sequence had SYNTAX ERRORS:\n"
                    + "\n".join(syntax_errors)
                    + f"\nThis was the sequence you returned:\n{json.dumps(sequence, indent=2)}\n"
                    "Fix the syntax and regenerate a new valid JSON dictionary."
                )
                print(err_block)
                prompt += err_block
                continue

            # Stage 3: Semantic check
            semantic_ok, semantic_errors = self.pv.validate_semantic(sequence['sequence'])
            print("Semantic OK:", semantic_ok)

            if not semantic_ok:
                num_semantic_errors += 1
                err_block = (
                    "\nYour previous sequence had SEMANTIC ERRORS:\n"
                    + "\n".join(semantic_errors)
                    + f"\nThis was the sequence you returned:\n{json.dumps(sequence, indent=2)}\n"
                    "Fix the logical errors and regenerate."
                )
                print(err_block)
                prompt += err_block
                continue
            
            valid_seq = True
            print(f"✓ VALID SEQUENCE FOUND after {attempts} attempts")
            return sequence, attempts, num_syntax_errors, num_semantic_errors
        
        return None, attempts, num_syntax_errors, num_semantic_errors
    
def main():

    env_generator = fraud_env.FraudEnv()
    env = env_generator.create_environment()
    
    # Generate fraud sequence
    planner = LLMPlanner(env)
    print(planner.generate_valid_fraud_seq())
    
    

if __name__ == "__main__":
    main()