"""
Universal Rules Validator - Entity Capability Based
Works with any LLM-generated action types
Focuses on what entities CAN and CANNOT do, not predefined action lists
"""

from pydantic import BaseModel
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json
import re


class EntityType(str, Enum):
    INDIVIDUAL = "individual"
    FRAUDSTER = "fraudster"
    BANK = "bank"
    ACCOUNT = "account"
    ORGANIZATION = "organization"
    TELECOM = "telecom"
    GOVERNMENT = "government"
    MERCHANT = "merchant"


class Entity(BaseModel):
    name: str
    type: EntityType
    
    def is_account(self) -> bool:
        return self.type == EntityType.ACCOUNT
    
    def is_human(self) -> bool:
        return self.type in {EntityType.INDIVIDUAL, EntityType.FRAUDSTER}
    
    def is_organization(self) -> bool:
        return self.type in {
            EntityType.BANK, EntityType.ORGANIZATION, 
            EntityType.TELECOM, EntityType.GOVERNMENT, EntityType.MERCHANT
        }


class ParsedAction(BaseModel):
    """Parsed action components"""
    subject: str
    action_type: str
    object: str
    channel: str
    details: str


class ParsedTransaction(BaseModel):
    """Parsed transaction components"""
    from_account: str
    payment_type: str
    to_account: str
    amount: float


class UniversalRulesValidator:
    """
    Validates based on entity capabilities, not predefined actions.
    Works with any action type the LLM generates.
    """
    
    def __init__(self, entity_registry: Dict[str, Entity]):
        self.entity_registry = entity_registry
    
    def requires_human_agency(self, action_type: str, channel: str) -> bool:
        """
        Determine if action requires human decision-making and communication.
        Based on keywords in action type and channel.
        """
        action_lower = action_type.lower()
        channel_lower = channel.lower()
        
        # Communication channels that require humans
        human_channels = ['call', 'phone', 'email', 'sms', 'text', 'chat', 'voice', 'in-person', 'meeting']
        if any(ch in channel_lower for ch in human_channels):
            return True
        
        # Actions that inherently require human agency
        human_actions = [
            'phish', 'imperson', 'pretend', 'pose', 'deceiv', 'trick', 'manipulat',
            'convince', 'persuad', 'social engineer', 'lie', 'claim', 'request',
            'ask', 'call', 'contact', 'speak', 'talk', 'discuss', 'negotiate'
        ]
        if any(kw in action_lower for kw in human_actions):
            return True
        
        return False
    
    def is_information_submission(self, action_type: str) -> bool:
        """
        Determine if action is about providing/sending information.
        Only humans can decide to submit their own information.
        """
        action_lower = action_type.lower()
        
        submission_keywords = [
            'submit', 'send', 'provide', 'give', 'share', 'reveal', 
            'disclose', 'tell', 'supply', 'furnish'
        ]
        
        # Check if it's about information/credentials
        info_keywords = ['info', 'data', 'credential', 'password', 'ssn', 'dob', 'detail']
        
        has_submission = any(kw in action_lower for kw in submission_keywords)
        has_info = any(kw in action_lower for kw in info_keywords)
        
        return has_submission and has_info
    
    def targets_human_psychology(self, action_type: str) -> bool:
        """
        Determine if action targets human psychology/behavior.
        You can't manipulate or trick an inanimate object.
        """
        action_lower = action_type.lower()
        
        psychological_actions = [
            'phish', 'social engineer', 'manipulat', 'trick', 'deceiv',
            'convince', 'persuad', 'imperson', 'pretend', 'scam'
        ]
        
        return any(kw in action_lower for kw in psychological_actions)
    
    def is_identity_based(self, action_type: str) -> bool:
        """
        Determine if action involves stealing/using identity.
        Only humans have identities that can be stolen.
        """
        action_lower = action_type.lower()
        return 'identity' in action_lower or 'impersonat' in action_lower
    
    def is_technical_system_action(self, action_type: str) -> bool:
        """
        Determine if action is purely technical/system-based.
        These might not require human agency.
        """
        action_lower = action_type.lower()
        
        technical_keywords = [
            'takeover', 'access', 'login', 'authenticate', 'hack', 'breach',
            'exploit', 'inject', 'query', 'request', 'api', 'database'
        ]
        
        return any(kw in action_lower for kw in technical_keywords)
    
    # ========================================================================
    # VALIDATION RULES
    # ========================================================================
    
    def validate_action(self, action: ParsedAction) -> Tuple[bool, Optional[str]]:
        """
        Apply universal capability-based rules.
        Returns: (is_valid, error_message)
        """
        
        subject_entity = self.entity_registry.get(action.subject)
        object_entity = self.entity_registry.get(action.object)
        
        if not subject_entity:
            return False, f"Unknown subject entity: {action.subject}"
        if not object_entity:
            return False, f"Unknown object entity: {action.object}"
        
        # RULE 1: Accounts cannot perform actions requiring human agency
        if subject_entity.is_account() and self.requires_human_agency(action.action_type, action.channel):
            return False, (
                f"Account '{action.subject}' cannot perform '{action.action_type}' via '{action.channel}'. "
                f"This action requires human agency (making calls, sending emails, communicating). "
                f"Change subject to a person or fraudster."
            )
        
        # RULE 2: Only humans can submit their own information
        if self.is_information_submission(action.action_type):
            if not subject_entity.is_human():
                return False, (
                    f"Only people can submit information, not {subject_entity.type.value} '{action.subject}'. "
                    f"Information submission requires conscious decision-making."
                )
        
        # RULE 3: Cannot target accounts with psychological manipulation
        if object_entity.is_account() and self.targets_human_psychology(action.action_type):
            return False, (
                f"Cannot perform '{action.action_type}' on account '{action.object}'. "
                f"This action targets human psychology/behavior. "
                f"Change object to the person who owns the account."
            )
        
        # RULE 4: Identity theft/impersonation targets humans or organizations, not accounts
        if self.is_identity_based(action.action_type):
            if object_entity.is_account():
                return False, (
                    f"Cannot perform '{action.action_type}' on account '{action.object}'. "
                    f"Identity-based actions target people or organizations, not accounts."
                )
        
        # RULE 5: Accounts can only perform technical actions on other accounts
        if subject_entity.is_account() and object_entity.is_account():
            if not self.is_technical_system_action(action.action_type):
                return False, (
                    f"Account '{action.subject}' cannot perform '{action.action_type}' on account '{action.object}'. "
                    f"Accounts can only have technical relationships (access, transfer). "
                    f"For money transfers, use transaction() syntax."
                )
        
        # RULE 6: General check - accounts should rarely be action subjects
        # Allow technical actions but flag anything else
        if subject_entity.is_account():
            if not self.is_technical_system_action(action.action_type):
                # This is a soft warning - might be valid but unusual
                # Return as valid but could be logged for review
                pass
        
        return True, None
    
    def validate_transaction(self, trans: ParsedTransaction) -> Tuple[bool, Optional[str]]:
        """
        Validate transaction - must be account to account
        """
        
        from_entity = self.entity_registry.get(trans.from_account)
        to_entity = self.entity_registry.get(trans.to_account)
        
        if not from_entity:
            return False, f"Unknown from entity: {trans.from_account}"
        if not to_entity:
            return False, f"Unknown to entity: {trans.to_account}"
        
        # RULE 7: Transactions must be between accounts
        if not from_entity.is_account():
            return False, (
                f"Transaction source must be an account, not {from_entity.type.value} '{trans.from_account}'. "
                f"Use the account belonging to {trans.from_account}."
            )
        
        if not to_entity.is_account():
            return False, (
                f"Transaction destination must be an account, not {to_entity.type.value} '{trans.to_account}'. "
                f"Use the account belonging to {trans.to_account}."
            )
        
        return True, None
    
    # ========================================================================
    # SEQUENCE VALIDATION
    # ========================================================================
    
    def parse_step(self, step: str) -> Tuple[str, dict]:
        """
        Parse a step string into type and components.
        Returns: (step_type, parsed_data)
        """
        step = step.strip()
        
        if step.startswith('action('):
            # Extract components: action(subject, action_type, object, channel, details)
            inner = step[7:-1]  # Remove "action(" and ")"
            parts = []
            current = ""
            paren_depth = 0
            
            for char in inner:
                if char == ',' and paren_depth == 0:
                    parts.append(current.strip())
                    current = ""
                else:
                    if char == '(':
                        paren_depth += 1
                    elif char == ')':
                        paren_depth -= 1
                    current += char
            parts.append(current.strip())
            
            if len(parts) != 5:
                return 'invalid', {}
            
            return 'action', {
                'subject': parts[0],
                'action_type': parts[1],
                'object': parts[2],
                'channel': parts[3],
                'details': parts[4]
            }
        
        elif step.startswith('transaction('):
            # Extract components: transaction(from, type, to, amount)
            inner = step[12:-1]  # Remove "transaction(" and ")"
            parts = [p.strip() for p in inner.split(',')]
            
            if len(parts) != 4:
                return 'invalid', {}
            
            return 'transaction', {
                'from_account': parts[0],
                'payment_type': parts[1],
                'to_account': parts[2],
                'amount': float(parts[3])
            }
        
        return 'invalid', {}
    
    def validate_semantic(self, sequence: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate entire sequence from JSON format.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        
        for i, step in enumerate(sequence):
            step_type, parsed_data = self.parse_step(step)
            
            if step_type == 'invalid':
                errors.append(f"Step {i}: Failed to parse step")
                continue
            
            if step_type == 'action':
                try:
                    action = ParsedAction(**parsed_data)
                    is_valid, error = self.validate_action(action)
                    if not is_valid:
                        errors.append(f"Step {i}: {error}")
                except Exception as e:
                    errors.append(f"Step {i}: {str(e)}")
            
            elif step_type == 'transaction':
                try:
                    trans = ParsedTransaction(**parsed_data)
                    is_valid, error = self.validate_transaction(trans)
                    if not is_valid:
                        errors.append(f"Step {i}: {error}")
                except Exception as e:
                    errors.append(f"Step {i}: {str(e)}")
        
        return len(errors) == 0, errors
    
    def validate_syntax(self, sequence: List[str]) -> Tuple[bool, List[str]]:
        """
        Validates entire syntax of entire sequence
        Returns: (is_valid, list of errors)
        """
        errors = []

        for i, step in enumerate(sequence):
            step_type, parsed_data = self.parse_step(step)
            
            if step_type == 'invalid':
                errors.append(f"Step {i}: Failed to parse step")
                continue

            if step_type == "action":
                if parsed_data['subject'] not in self.entity_registry:
                    errors.append(f"Step {i}: {parsed_data['subject']} is not a valid entity.")
                if parsed_data['object'] not in self.entity_registry:
                    errors.append(f"Step {i}: {parsed_data['object']} is not a valid entity.")

            if step_type == "transaction":
                if parsed_data['from_account'] not in self.entity_registry:
                    errors.append(f"Step {i}: {parsed_data['from_account']} is not a valid entry.")
                if parsed_data['to_account'] not in self.entity_registry:
                    errors.append(f"Step {i}: {parsed_data['to_account']} is not a valid entry.")

        
        return len(errors) == 0, errors



# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Setup entity registry
    entity_registry = {
        "sally": Entity(name="sally", type=EntityType.INDIVIDUAL),
        "fraudster": Entity(name="fraudster", type=EntityType.FRAUDSTER),
        "fishmaster": Entity(name="fishmaster", type=EntityType.FRAUDSTER),
        "govco": Entity(name="govco", type=EntityType.FRAUDSTER),
        "bank": Entity(name="bank", type=EntityType.BANK),
        "bankofamerica": Entity(name="bankofamerica", type=EntityType.BANK),
        "tmobile": Entity(name="tmobile", type=EntityType.TELECOM),
        "insuranceco": Entity(name="insuranceco", type=EntityType.ORGANIZATION),
        "acc_sally": Entity(name="acc_sally", type=EntityType.ACCOUNT),
        "acc_fraudster": Entity(name="acc_fraudster", type=EntityType.ACCOUNT),
        "acc_fishmaster": Entity(name="acc_fishmaster", type=EntityType.ACCOUNT),
        "acc_govco": Entity(name="acc_govco", type=EntityType.ACCOUNT),
        "acc_bank": Entity(name="acc_bank", type=EntityType.ACCOUNT),
        "acc_tmobile": Entity(name="acc_tmobile", type=EntityType.ACCOUNT),
        "acc_insuranceco": Entity(name="acc_insuranceco", type=EntityType.ACCOUNT),
    }
    
    validator = UniversalRulesValidator(entity_registry)
    
    # Test cases in JSON format
    test_cases = [
        {
            "name": "✅ VALID - Good fraud sequence",
            "data": {
                "sequence": [
                    "action(govco, Impersonation, george, Call, Posed as IRS agent)",
                    "action(sally, Sensitive Info Submission, govco, SMS, sent SSN + DOB)",
                    "action(govco, Social engineering, bankofamerica, Call, Requested account access)",
                    "transaction(acc_sally, FAST Payment, acc_govco, 3000.00)"
                ]
            }
        },
        {
            "name": "❌ INVALID - Your bad example",
            "data": {
                "sequence": [
                    "action(acc_sally, sim swap, acc_tmobile, call, requested number change)",
                    "action(acc_tmobile, account takeover, acc_sally, sms, sent login credentials)",
                    "action(acc_insuranceco, phishing, fishmaster, email, spoofed insurance company email)",
                    "action(fishmaster, identity theft, acc_insuranceco, call, requested sensitive info)",
                    "transaction(acc_insuranceco, fast payment, acc_fishmaster, 5000.00)"
                ]
            }
        },
        {
            "name": "❌ INVALID - Transaction to person",
            "data": {
                "sequence": [
                    "transaction(acc_sally, FAST Payment, fraudster, 1000.00)"
                ]
            }
        },
        {
            "name": "✅ VALID - Novel LLM-generated action",
            "data": {
                "sequence": [
                    "action(fraudster, spoofed caller ID attack, sally, phone, displayed fake bank number)",
                    "action(sally, credential disclosure, fraudster, phone, revealed account PIN)",
                    "transaction(acc_sally, wire transfer, acc_fraudster, 5000.00)"
                ]
            }
        }
    ]

    print("=" * 80)
    print("SYNTAX RULES VALIDATION")
    print("=" * 80)

    for test_case in test_cases:
        is_valid, errors = validator.validate_syntax(test_case['data']['sequence'])
        print(f"Valid: {is_valid}")
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  • {error}")
    
    print("=" * 80)
    print("SEMANTIC RULES VALIDATION")
    print("=" * 80)
    
    for test_case in test_cases:
        print(f"\nExpected: {test_case['name']}")
        print("-" * 80)
        
        is_valid, errors = validator.validate_semantic(test_case['data']['sequence'])
        
        print(f"Valid: {is_valid}")
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  • {error}")
