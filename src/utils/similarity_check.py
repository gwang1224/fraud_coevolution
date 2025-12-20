import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

model = SentenceTransformer("all-MiniLM-L6-v2")

def sim_check():

    with open('data/coev/coev_seq_v2.json', 'r') as f:
        data = json.load(f)

        fraud_data = [", ".join(value.get("sequence")) for key, value in data.items() if value.get("label") == "legit"]

        embeddings = model.encode(fraud_data, convert_to_numpy=True, normalize_embeddings=True)
        cos_matrix = cosine_similarity(embeddings)

        # upper_triangular_matrix = np.triu(cos_matrix, k=1)

        # avg_similarity = np.mean(upper_triangular_matrix)
        n = cos_matrix.shape[0]
        iu = np.triu_indices(n, k=1)
        pairwise_sims = cos_matrix[iu]
        avg_similarity = pairwise_sims.mean()
        return upper_triangular_matrix, avg_similarity
    
# def sim_check2():

with open('data/coev/coev_seq_v2.json', 'r') as f:
    data = json.load(f)
    fraud_data = [value.get("sequence") for key, value in data.items() if value.get("label") == "legit"]

    data_no_desc = []

    for seq in fraud_data:
        desc_removed = ""
        for act in seq:
            if act.startswith("action("):
                desc_removed += ",".join(act.split(",")[:-1]) + ")" + ", "
            else:
                desc_removed += act
        data_no_desc.append(desc_removed)

    embeddings = model.encode(data_no_desc, convert_to_numpy=True, normalize_embeddings=True)
    cos_matrix = cosine_similarity(embeddings)

    # upper_triangular_matrix = np.triu(cos_matrix, k=1)

    # avg_similarity = np.mean(upper_triangular_matrix)
    # print(upper_triangular_matrix)
    n = cos_matrix.shape[0]
    iu = np.triu_indices(n, k=1)
    pairwise_sims = cos_matrix[iu]
    avg_similarity = pairwise_sims.mean()
    print(avg_similarity)


      
        

        