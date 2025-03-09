from retrieve_all_papers import get_all_papers_from_db
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity



papers = get_all_papers_from_db()

print("""------------------------------------------------------
      
        ------------------------------------------------------
      
      """)

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def average_embeddings(papers):
    embeddings = [get_embedding(paper['summary']) for paper in papers]
    return np.mean(embeddings, axis=0)

def sim_score(user_preference_vector,check_paper):
    #this needs to be abstract of new paper
    similarity_score = cosine_similarity([user_preference_vector], [check_paper])[0][0]

    print("Similarity Score:", similarity_score)

def update_user_vector(user_vector, new_embedding, alpha=0.7):
    # Convert lists to numpy arrays for element-wise operations
    user_vector = np.array(user_vector)
    new_embedding = np.array(new_embedding)
    # Compute weighted update
    updated_vector = alpha * user_vector + (1 - alpha) * new_embedding
    return updated_vector.tolist() 

check_paper = get_embedding("i like toes")
liked_paper = get_embedding("toes are my favourite")

user_preference_vector = average_embeddings(papers)
sim_score(user_preference_vector,check_paper)

user_preference_vector = update_user_vector(user_preference_vector, liked_paper)
sim_score(user_preference_vector,check_paper)
