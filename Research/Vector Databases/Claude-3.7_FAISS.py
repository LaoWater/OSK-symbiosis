import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import json
import random
from datetime import datetime, timedelta


# ----- 1. Data Generation -----

# Function to generate realistic real estate data
def generate_real_estate_data(num_properties=100):
    # Property types and features
    property_types = ['Apartment', 'House', 'Condo', 'Townhouse', 'Duplex']
    neighborhoods = ['Downtown', 'Westside', 'Northpark', 'Eastdale', 'Southbay', 'Riverside']
    features = [
        'hardwood floors', 'stainless steel appliances', 'granite countertops',
        'walk-in closet', 'garden', 'balcony', 'fireplace', 'high ceilings',
        'open floor plan', 'recently renovated', 'smart home features',
        'swimming pool', 'garage', 'backyard', 'home office space'
    ]

    properties = []

    for i in range(num_properties):
        # Basic property details
        prop_type = random.choice(property_types)
        bedrooms = random.randint(1, 5)
        bathrooms = random.randint(1, 4)
        sq_ft = random.randint(500, 3500)
        neighborhood = random.choice(neighborhoods)

        # Price based on size and type (with some randomness)
        base_price = sq_ft * random.uniform(2.5, 4.5)
        if prop_type in ['House', 'Townhouse']:
            base_price *= 1.3
        price = int(base_price * 1000) + random.randint(-50000, 50000)

        # Random property features (3-8 features)
        num_features = random.randint(3, 8)
        property_features = random.sample(features, num_features)

        # Generate listing date (within last 60 days)
        days_ago = random.randint(1, 60)
        list_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

        # Create description
        description = f"Beautiful {bedrooms} bedroom, {bathrooms} bathroom {prop_type.lower()} in {neighborhood}. "
        description += f"This {sq_ft} sq ft property features {', '.join(property_features[:-1])}"
        if len(property_features) > 1:
            description += f" and {property_features[-1]}. "
        else:
            description += ". "

        # Add some random phrases to description
        phrases = [
            "Perfect for families or professionals.",
            "Ideal location close to shops and restaurants.",
            "Move-in ready with great natural light.",
            "Don't miss this opportunity!",
            "Newly listed and won't last long at this price.",
            "Modern design with attention to detail.",
            "Nestled in a quiet, friendly neighborhood."
        ]
        description += random.choice(phrases)

        # Create property object
        property_obj = {
            'id': i + 1,
            'type': prop_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sq_ft': sq_ft,
            'price': price,
            'neighborhood': neighborhood,
            'features': property_features,
            'description': description,
            'list_date': list_date
        }

        properties.append(property_obj)

    return properties


# ----- 2. Vector Database Setup -----

class RealEstateVectorDB:
    def __init__(self, properties=None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for embeddings
        self.properties = properties if properties else []
        self.property_df = None
        self.index = None
        self.embeddings = None

        if properties:
            self.create_index()

    def add_properties(self, properties):
        """Add properties to the database and update the index"""
        self.properties = properties
        self.create_index()

    def create_index(self):
        """Create a FAISS index from property descriptions"""
        # Create DataFrame for easier manipulation
        self.property_df = pd.DataFrame(self.properties)

        # Extract descriptions for embedding
        descriptions = self.property_df['description'].tolist()

        # Generate embeddings
        self.embeddings = self.model.encode(descriptions)

        # Create FAISS index (using L2 distance)
        dimension = self.embeddings.shape[1]  # Get embedding dimension
        self.index = faiss.IndexFlatL2(dimension)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)

        # Add vectors to the index
        self.index.add(self.embeddings)

        print(f"Created vector index with {len(self.properties)} properties")

    def search_similar_properties(self, query_text, top_k=5):
        """Find properties similar to the query text"""
        # Encode the query
        query_embedding = self.model.encode([query_text])

        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search the index
        distances, indices = self.index.search(query_embedding, top_k)

        # Get the matching properties
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.properties):  # Safety check
                property_data = self.properties[idx]
                similarity_score = 1 - distances[0][i]  # Convert L2 distance to similarity score
                result = {
                    'property': property_data,
                    'similarity_score': float(similarity_score)
                }
                results.append(result)

        return results

    def filter_and_search(self, query_text, filters=None, top_k=5):
        """Search with additional filtering criteria"""
        # First, filter properties based on criteria
        filtered_indices = []

        for i, prop in enumerate(self.properties):
            # Skip if it doesn't match any of the filters
            if filters:
                matches_filters = True
                for key, value in filters.items():
                    if key == 'min_price' and prop['price'] < value:
                        matches_filters = False
                        break
                    elif key == 'max_price' and prop['price'] > value:
                        matches_filters = False
                        break
                    elif key == 'min_bedrooms' and prop['bedrooms'] < value:
                        matches_filters = False
                        break
                    elif key == 'neighborhood' and prop['neighborhood'] != value:
                        matches_filters = False
                        break
                    elif key == 'property_type' and prop['type'] != value:
                        matches_filters = False
                        break

                if not matches_filters:
                    continue

            filtered_indices.append(i)

        # If no properties match filters, return empty list
        if not filtered_indices:
            return []

        # Create a temporary index with only the filtered properties
        temp_embeddings = self.embeddings[filtered_indices]
        temp_index = faiss.IndexFlatL2(temp_embeddings.shape[1])
        temp_index.add(temp_embeddings)

        # Encode and search
        query_embedding = self.model.encode([query_text])
        faiss.normalize_L2(query_embedding)

        # Get only as many results as available (up to top_k)
        k = min(top_k, len(filtered_indices))
        distances, indices = temp_index.search(query_embedding, k)

        # Map back to original indices and get properties
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(filtered_indices):  # Safety check
                original_idx = filtered_indices[idx]
                property_data = self.properties[original_idx]
                similarity_score = 1 - distances[0][i]
                result = {
                    'property': property_data,
                    'similarity_score': float(similarity_score)
                }
                results.append(result)

        return results


# ----- 3. Demo Implementation -----

def main():
    # Generate sample data
    print("Generating real estate property data...")
    properties = generate_real_estate_data(200)

    # Save generated data to a JSON file for reference
    with open('real_estate_data.json', 'w') as f:
        json.dump(properties, f, indent=2)

    # Create vector database
    print("Creating vector database...")
    vector_db = RealEstateVectorDB(properties)

    # Example searches
    print("\n--- Demo: Semantic Property Search ---\n")

    # Search 1: Simple semantic search
    query = "Modern apartment with office space for remote work"
    results = vector_db.search_similar_properties(query, 3)

    print(f"Search: '{query}'")
    print("Top 3 matches:")
    for i, result in enumerate(results):
        property_data = result['property']
        score = result['similarity_score']
        print(f"{i + 1}. {property_data['type']} - ${property_data['price']:,} - " +
              f"{property_data['bedrooms']}bd/{property_data['bathrooms']}ba - " +
              f"Score: {score:.2f}")
        print(f"   Description: {property_data['description'][:100]}...")

    # Search 2: Filtered search
    print("\n--- Demo: Filtered Semantic Search ---\n")

    query = "Spacious home with outdoor space"
    filters = {
        'min_bedrooms': 3,
        'min_price': 800000,
        'property_type': 'House'
    }

    results = vector_db.filter_and_search(query, filters, 3)

    print(f"Search: '{query}' with filters: {filters}")
    print("Top 3 matches:")
    for i, result in enumerate(results):
        property_data = result['property']
        score = result['similarity_score']
        print(f"{i + 1}. {property_data['type']} - ${property_data['price']:,} - " +
              f"{property_data['bedrooms']}bd/{property_data['bathrooms']}ba - " +
              f"Score: {score:.2f}")
        print(f"   Description: {property_data['description'][:100]}...")

    # Search 3: Neighborhood-specific search
    print("\n--- Demo: Neighborhood-Specific Search ---\n")

    query = "Cozy, quiet place with modern features"
    filters = {
        'neighborhood': 'Riverside'
    }

    results = vector_db.filter_and_search(query, filters, 3)

    print(f"Search: '{query}' with filters: {filters}")
    print("Top 3 matches:")
    for i, result in enumerate(results):
        property_data = result['property']
        score = result['similarity_score']
        print(f"{i + 1}. {property_data['type']} - ${property_data['price']:,} - " +
              f"{property_data['bedrooms']}bd/{property_data['bathrooms']}ba - " +
              f"Score: {score:.2f}")
        print(f"   Description: {property_data['description'][:100]}...")


if __name__ == "__main__":
    main()