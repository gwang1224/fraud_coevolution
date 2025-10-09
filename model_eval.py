"""
Model Evaluation Script

Description:
-------------
Evaluates multiple LLMs for their ability to generate valid FAST payment fraud sequences
using the LLMPlanner class from llmplanner.py. It runs multiple samples for each model,
validates the output, and logs performance statistics.

Evaluation Metrics:
-------------------
(1) Valid Sequences - number of sequences that pass regex/entity validation.
(2) Average Steps - average number of steps per valid sequence.
(3) Error Counts - number of failures for each category:
      - Input type errors (invalid JSON / malformed output)
      - Action errors (invalid Action() steps)
      - Transaction errors (invalid Transaction() steps)
      - End sequence errors (sequence not ending with Transaction)

Current Models:
---------------
- chevalblanc/gpt-4o-mini
- llama3.2
- mistral
- gemma3:4b

Outputs:
--------
- Prints progress and model statistics to console.
- Saves summary table to "model_eval_results.csv" in the working directory.

Usage:
------
Run this script after ensuring llmplanner.py is functional.
Example:
    $ python model_eval.py
"""

import pandas as pd
import llmplanner as gen

# Models to test
models = ['chevalblanc/gpt-4o-mini', 'llama3.2', 'mistral','gemma3:4b']

samples = 100
results = []
gen_agent = gen.LLMPlanner()


for model in models:
    valid_count = 0
    total_len = 0

    #stats
    input_type = 0
    er_action = 0
    er_trans = 0
    er_end_seq = 0

    for i in range(samples):
        # Gen sequence
        print(f"\nGenerating sequence {i}...")
        response = gen_agent.generate_sequence(model)
        print(response)

        if response is None:
            input_type += 1
        else:
            valid, rof = gen_agent.validate(response)
            if valid == False:
                if rof == "input":
                    input_type += 1
                elif rof == "action":
                    er_action += 1
                elif rof == "transaction":
                    er_trans += 1
                elif rof == "end":
                    er_end_seq += 1
            else:
                valid_count += 1
                print("Passed :)") 

                # Note Sequence length
                total_len += len(response['sequence'])

    if valid_count > 0:
        avg_len = total_len/valid_count
    else:
        avg_len = 0

    results.append({
        'Model': model,
        'Valid Sequences': valid_count,
        'Total Samples': samples,
        'Avg Steps': avg_len,
        'Error: Input type': input_type,
        'Error: Action': er_action,
        'Error: Transaction': er_trans,
        'Error: End sequence': er_end_seq
    })

df = pd.DataFrame(results)
print(df)
df.to_csv("model_eval_results2.csv", index=False)
