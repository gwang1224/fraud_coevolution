import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

model = SentenceTransformer("all-MiniLM-L6-v2")

def prep_data(file, strip=False):
    """
    Prepares sequences by removing description and action/transaction start
    
    :param file: Description
    :param strip: Description
    """
    with open(file, 'r') as f:
        data = json.load(f)
        data = [", ".join(value.get("sequence")) for key, value in data.items() if value.get("label") == "fraud"]

        if strip == True:
            data_no_desc = []

            for seq in data:
                print(seq)
                for act in seq:
                    if act.startswith("action("):
                        desc_removed += ",".join(act.split(",")[5:-1]) + ")" + ", "
                        print(desc_removed + '\n')
                    else:
                        desc_removed += act
                data_no_desc.append(desc_removed)
            return data_no_desc
    return data


def sim_check_full_seq(file):
    """
    Docstring for sim_check_full_seq
    
    :param file: Description
    """
    with open(file, 'r') as f:
        data = json.load(f)

        fraud_data = [", ".join(value.get("sequence")) for key, value in data.items() if value.get("label") == "fraud"]

        embeddings = model.encode(fraud_data, convert_to_numpy=True, normalize_embeddings=True)
        cos_matrix = cosine_similarity(embeddings)

        n = cos_matrix.shape[0]
        iu = np.triu_indices(n, k=1)
        pairwise_sims = cos_matrix[iu]
        avg_similarity = pairwise_sims.mean()
        return avg_similarity

def sim_check2():
    with open('data/coev/coev_seq_v2.json', 'r') as f:
        data = json.load(f)
        fraud_data = [value.get("sequence") for key, value in data.items() if value.get("label") == "fraud"]

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

        n = cos_matrix.shape[0]
        iu = np.triu_indices(n, k=1)
        pairwise_sims = cos_matrix[iu]
        avg_similarity = pairwise_sims.mean()
        return avg_similarity
    
def sim_check3():
    with open('data/coev/coev_seq_v2.json', 'r') as f:
        data = json.load(f)
        fraud_data = [value.get("sequence") for key, value in data.items() if value.get("label") == "fraud"]
        legit_data = [value.get("sequence") for key, value in data.items() if value.get("label") == "legit"]


        fraud_data_no_desc = []
        legit_data_no_desc = []

        for seq in fraud_data:
            desc_removed = ""
            for act in seq:
                if act.startswith("action("):
                    desc_removed += ",".join(act.split(",")[:-1]) + ")" + ", "
                else:
                    desc_removed += act
            fraud_data_no_desc.append(desc_removed)

        for seq in legit_data:
            desc_removed = ""
            for act in seq:
                if act.startswith("action("):
                    desc_removed += ",".join(act.split(",")[:-1]) + ")" + ", "
                else:
                    desc_removed += act
            legit_data_no_desc.append(desc_removed)

        embeddings1 = model.encode(fraud_data_no_desc, convert_to_numpy=True, normalize_embeddings=True)
        embeddings2 = model.encode(legit_data_no_desc, convert_to_numpy=True, normalize_embeddings=True)

        cos_matrix = cosine_similarity(embeddings1,embeddings2)

        n = cos_matrix.shape[0]
        iu = np.triu_indices(n, k=1)
        pairwise_sims = cos_matrix[iu]
        avg_similarity = pairwise_sims.mean()
        return cos_matrix, avg_similarity
    
# sim_check_full_seq('data/coev/coev_seq_v2.json')
prep_data('data/coev/coev_seq_v2.json', strip=True)
      
        

        