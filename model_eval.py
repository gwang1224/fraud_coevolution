"""
Model evaluation script

Purpose
- Determine which large language model is best for generating fast payment sequences
- Generates statistics based on
    (1) # of valid sequences
    (2)

Current models
- 'chevalblanc/gpt-4o-mini'

Usage

Outputs
   
Notes

"""

import pandas as pd
import llmplanner as gen

# Models to test
models = ['chevalblanc/gpt-4o-mini']

samples = 5
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
df.to_csv("model_eval_results.csv", index=False)
