import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ----------------------------------------
# 1. Define our dataset of travel destinations.
# Each destination has a description capturing its vibe.
# ----------------------------------------
destinations = [
    {
        "name": "Bali, Indonesia",
        "description": "A tropical paradise with stunning beaches, vibrant culture, and lush green rice terraces."
    },
    {
        "name": "Reykjavik, Iceland",
        "description": "A unique destination featuring dramatic landscapes, geysers, waterfalls, and the Northern Lights."
    },
    {
        "name": "Paris, France",
        "description": "The city of love known for its art, cuisine, historical monuments, and charming streets."
    },
    {
        "name": "Maldives",
        "description": "An archipelago in the Indian Ocean with crystal-clear waters, luxurious overwater bungalows, and vibrant marine life."
    },
    {
        "name": "Kyoto, Japan",
        "description": "A city that blends ancient temples, traditional tea houses, and beautiful gardens with a modern twist."
    },
    {
        "name": "Cancún, Mexico",
        "description": "Famous for its white sandy beaches, turquoise waters, and lively nightlife, perfect for a relaxing escape."
    },
    {
        "name": "New York City, USA",
        "description": "A bustling metropolis with iconic landmarks, diverse neighborhoods, and endless entertainment options."
    }
]

# ----------------------------------------
# 2. Load a pre-trained sentence transformer model.
# The model will convert destination descriptions into dense vectors.
# ----------------------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings for each destination description.
descriptions = [dest["description"] for dest in destinations]
embeddings = model.encode(descriptions, convert_to_numpy=True)

# Determine embedding dimension (e.g., 384 for this model)
d = embeddings.shape[1]

# ----------------------------------------
# 3. Build the FAISS index as our vector database.
# We use an IndexFlatL2 for simplicity (exact search using L2 distance).
# ----------------------------------------
index = faiss.IndexFlatL2(d)
index.add(embeddings)


# ----------------------------------------
# 4. Function to query the vector database.
# Given a natural language query, the system returns the top-N similar destinations.
# ----------------------------------------
def recommend_destinations(query, top_k=3):
    # Compute the embedding for the query.
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search for similar destinations.
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, distance in zip(indices[0], distances[0]):
        results.append({
            "name": destinations[idx]["name"],
            "description": destinations[idx]["description"],
            "distance": float(distance)
        })
    return results


# ----------------------------------------
# 5. Example: User Query and Recommendation
# Let's simulate a user query for a relaxing tropical beach getaway.
# ----------------------------------------
if __name__ == "__main__":
    user_query = "I want a relaxing tropical beach getaway with clear waters and sun."
    recommendations = recommend_destinations(user_query, top_k=3)

    print("User Query:", user_query)
    print("\nRecommended Travel Destinations:")
    for rec in recommendations:
        print(
            f"---\nName: {rec['name']}\nDescription: {rec['description']}\nSimilarity Score (lower is better): {rec['distance']:.4f}")
