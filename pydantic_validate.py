from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import List, Dict

# Suppose these come from your graph
EXISTING_ENTITIES = {"ScamGov", "Olivia", "BankOfAmerica", "acc_olivia", "acc_scamgov"}

# initial bank balances (you can load these from your environment)
BANK_BALANCES = {
    "acc_olivia": 5000.0,
    "acc_scamgov": 0.0
}


class SequenceModel(BaseModel):
    sequence: List[str] = Field(..., description="List of action/transaction strings")

    @field_validator("sequence")
    def validate_sequence(cls, seq):
        balances = BANK_BALANCES.copy()

        for s in seq:
            # 1- Check correct start/end
            if not (s.startswith("action(") or s.startswith("transaction(")):
                raise ValueError(f"Invalid start: {s}")
            if not s.endswith(")"):
                raise ValueError(f"Missing closing parenthesis: {s}")

            # 2- Parse contents
            inner = s[s.find("(") + 1 : s.rfind(")")]
            parts = [p.strip() for p in inner.split(",")]

            # 3- Validate action
            if s.startswith("action("):
                if len(parts) < 5:
                    raise ValueError(f"Action must have at least 5 parts: {s}")

                actor, intent, target, medium, desc = parts[:5]

                # (rule 1) Entities exist
                if actor not in EXISTING_ENTITIES:
                    raise ValueError(f"Unknown entity: {actor}")
                if target not in EXISTING_ENTITIES:
                    raise ValueError(f"Unknown entity: {target}")

            # 4- Validate transaction
            elif s.startswith("transaction("):
                if len(parts) != 4:
                    raise ValueError(f"Transaction must have exactly 4 parts: {s}")

                src, method, dst, amount_str = parts
                if src not in EXISTING_ENTITIES or dst not in EXISTING_ENTITIES:
                    raise ValueError(f"Unknown account in transaction: {s}")

                try:
                    amount = float(amount_str)
                except ValueError:
                    raise ValueError(f"Invalid amount: {amount_str}")

                # (rule 4) Update and check balances
                balances[src] = balances.get(src, 0.0) - amount
                balances[dst] = balances.get(dst, 0.0) + amount

                if balances[src] < 0:
                    raise ValueError(f"Negative balance detected for {src}: {balances[src]}")

        return seq
    

test_seq = {
  "sequence": [
    "action(ScamGov, Impersonation, Olivia, Call, Posed as IRS agent)",
    "action(Olivia, Sensitive Info Submission, ScamGov, SMS, sent SSN + DOB)",
    "action(ScamGov, Social engineering, BankOfAmerica, Call, a;lskdfj)",
    "transaction(acc_olivia, FAST Payment, acc_scamgov, 5000.00)"
  ]
}

Grace = SequenceModel(**test_seq)
print(Grace)