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
models = ['chevalblanc/gpt-4o-mini', 'llama3.2', 'mistral']

samples = 10
results = []
gen_model = gen.LLMPlanner()


for model in models:
    valid_count = 0
    avg_len = 0

    for i in range(samples):

        # Gen sequence
        print(f"\nGenerating sequence {i}...")
        response = gen_model.generate_sequence(model)

        # Validate sequence
        if gen_model.validate(response):
            valid_count += 1
            print("Passed.")

            # Sequence length
            length = len(response['sequence'])
            avg_len += length

    if valid_count > 0:
        avg_len = avg_len/valid_count

    results.append({
        'Model': model,
        'Valid Sequences': valid_count,
        'Total Samples': samples,
        'Avg Steps': avg_len
    })

df = pd.DataFrame(results)
print(df)
df.to_csv("model_eval_results.csv", index=False)
