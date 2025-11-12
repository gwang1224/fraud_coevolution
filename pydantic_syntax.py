from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Dict

class SequenceModel(BaseModel):
    sequence: List[str] = Field(..., description="List of action/transaction strings")

    @field_validator("sequence")
    def validate_sequence(cls, seq, info):
        ctx = info.context or {}
        existing_entities = set(ctx.get("entities", []))
        balances = dict(ctx.get("balances", {}))  # start from provided balances (may be empty)
        if not existing_entities:
            raise ValueError("No 'entities' provided in context for validation.")

        for s in seq:
            # 1- Check correct start/end
            if not (s.startswith("action(") or s.startswith("transaction(")):
                raise ValueError(f"Invalid start: {s}")
            if not s.endswith(")"):
                raise ValueError(f"Missing closing parenthesis: {s}")

            # 2- Parse contents
            inner = s[s.find("(") + 1 : s.rfind(")")]
            parts = [p.strip() for p in inner.split(",")]

            # 3- Validate action steps
            if s.startswith("action("):
                if len(parts) != 5:
                    raise ValueError(f"Action must have 5 elements. Action contains {len(parts)}\n{s}\n")

                entity1, intent, entity2, medium, desc = parts

                # (rule 1) Entities exist
                if entity1 not in existing_entities:
                    raise ValueError(f"Unknown entity: {entity1}")
                if entity2 not in existing_entities:
                    raise ValueError(f"Unknown entity: {entity2}")

            # 4- Validate transaction
            elif s.startswith("transaction("):
                if len(parts) != 4:
                    raise ValueError(f"Transaction must have 4 elements. Transaction contains {len(parts)}\n{s}\n")

                src, method, dst, amount_str = parts
                if src not in existing_entities or dst not in existing_entities:
                    raise ValueError(f"Unknown account in transaction: {s}")

                # CHECKS WHETHER ACCOUNT HAS BALANCE IS SUFFICIENT
                # maybe implement later
                # try:
                #     amount = float(amount_str)
                # except ValueError:
                #     raise ValueError(f"Invalid amount: {amount_str}")

                # # (rule 4) Update and check balances
                # balances[src] = balances.get(src, 0.0) - amount
                # balances[dst] = balances.get(dst, 0.0) + amount

                # if balances[src] < 0:
                #     raise ValueError(f"Negative balance detected for {src}: {balances[src]}")

        return seq
    

def main():
    env_entities = {"ScamGov", "Olivia", "BankOfAmerica", "acc_olivia", "acc_scamgov"}
    env_balances = {"acc_olivia": 5000.0, "acc_scamgov": 0.0}

    test = {'sequence': ['action(scamgov, social engineering, acc_sally, call, sent phishing link)', 'action(acc_sally, sensitive info submission, scamgov, sms, sent ssn + dob)', 'action(acc_sally, account takeover, firstfinancial, call, gained access to account)', 'action(firstfinancial, account compromise, acc_sally, call, triggered fraudulent transactions)', 'action(scamgov, sim swap, acc_grace, sms, switched phone number)', 'action(acc_grace, number porting issue, scamgov, call, inability to receive calls)', 'action(acc_grace, identity theft, scamco, call, stolen identity used for fraud)', 'transaction(acc_grace, fast payment, acc_scamgov, 10000.00)']}

    try:
        T = SequenceModel.model_validate(test, context={"entities": env_entities})
        print("✅ Validation passed")
    except Exception as e:
        print("❌ Validation failed:", e)

if __name__ == "__main__":
    main()
