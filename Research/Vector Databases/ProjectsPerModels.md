# Built on O3-mini-high 

# 1. Travel Destination Recommendation System

**Overview:**  
This project is a travel recommendation system that uses vector databases to deliver personalized travel suggestions. Instead of relying on simple keyword matching, it leverages natural language processing to understand the intent behind a user’s query and finds destinations that best match that intent.

**How It Works:**  

1. **Data Preparation:**  
   - A curated list of travel destinations is created, with each destination featuring a detailed description that captures its unique vibe and attractions.

2. **Generating Embeddings:**  
   - A pre-trained sentence transformer model (such as `all-MiniLM-L6-v2`) converts the text descriptions into high-dimensional numerical vectors (embeddings). These embeddings capture the semantic meaning of the descriptions.

3. **Indexing with FAISS:**  
   - The generated embeddings are stored in a FAISS index, a vector database that efficiently handles similarity searches in high-dimensional space.

4. **Query Processing:**  
   - When a user inputs a natural language query (e.g., "I want a relaxing tropical beach getaway"), the same transformer model converts the query into its embedding.

5. **Similarity Search:**  
   - The FAISS index is queried using the query embedding. It returns the top matching travel destinations based on the Euclidean distance between the query and destination embeddings.

6. **Delivering Recommendations:**  
   - The system outputs a list of recommended travel destinations that semantically align with the user’s query, providing more nuanced and context-aware suggestions than traditional keyword searches.

**Real-World Application:**  
This system is ideal for travel websites and mobile apps that aim to provide users with personalized travel recommendations. By understanding the semantic context of user queries, it offers more relevant suggestions—helping travelers discover destinations that truly match their desired experiences.


---

# 2. Semantic News Search with Vector Databases

This project demonstrates a real-world application of vector databases by building a semantic search engine for Hacker News headlines. It integrates web scraping, natural language processing, and vector indexing to efficiently retrieve news headlines that are semantically related to user queries.

## How It Works

1. **Web Scraping:**  
   The script fetches the Hacker News front page and extracts news headlines and URLs using Python's `requests` library and `BeautifulSoup` for HTML parsing.

2. **Semantic Embedding:**  
   Each headline is converted into a numerical vector representation using a pre-trained SentenceTransformer model (`all-MiniLM-L6-v2`). These embeddings capture the semantic meaning of the text.

3. **Vector Indexing with FAISS:**  
   The computed embeddings are stored in a FAISS index, which is optimized for fast similarity search in high-dimensional vector spaces.

4. **Interactive Semantic Search:**  
   Users can input a search query, which is embedded using the same model. The FAISS index then returns the most semantically similar headlines along with their similarity scores and URLs.

This project showcases how vector databases can enhance search functionality by understanding the semantic context, providing a scalable solution for real-time data retrieval.



# Built on Claude 3.7

# 1. Real Estate Property Matching System Using Vector Database

## Project Overview
This project demonstrates a real estate property recommendation system that leverages vector databases to match properties with user preferences based on both structured data and semantic meaning in property descriptions.

## How It Works

### 1. Data Processing
- The system generates or ingests real estate property data including both structured attributes (price, bedrooms, neighborhood) and unstructured text descriptions
- Each property description is converted into a numerical vector (embedding) using a pre-trained Sentence Transformer model
- These embeddings capture the semantic meaning of property descriptions, allowing for similarity comparisons

### 2. Vector Database Setup
- FAISS (Facebook AI Similarity Search) is used to create an efficient vector index
- Property embeddings are normalized and added to the index for fast similarity searching
- The index supports both pure semantic search and hybrid filtering options

### 3. Search Capabilities
- **Semantic Search**: Users can search in natural language (e.g., "modern apartment with office space for remote work")
- **Filtered Search**: Combines vector similarity with traditional filters (price ranges, bedroom counts, etc.)
- **Neighborhood-Specific Search**: Allows targeting specific areas while maintaining semantic matching

### 4. Results Ranking
- Properties are ranked by similarity score (how closely they match the semantic meaning of the query)
- Results include both property details and a confidence score for each match

This approach significantly improves upon traditional keyword-based property search by understanding context and semantic meaning, leading to more relevant property recommendations even when exact terms don't match.

---

# 2. Semantic Recipe Search with Vector Database

## Project Overview
A semantic recipe search engine that allows users to find recipes through natural language queries, ingredients they have on hand, and various filtering criteria. This system goes beyond traditional keyword matching by understanding the semantic meaning behind recipe descriptions and search queries.

## How It Works

1. **Data Collection**: Recipes are gathered (simulated API in this demo, but could be from web scraping or actual recipe APIs)

2. **Vector Embedding**: 
   - Each recipe is converted into a rich text description
   - A pre-trained sentence transformer model converts these descriptions into vector embeddings
   - These vectors capture semantic relationships between recipes

3. **Vector Database Indexing**:
   - FAISS (Facebook AI Similarity Search) creates an efficient index of all recipe vectors
   - Enables fast nearest-neighbor searching across thousands of recipes

4. **Search Capabilities**:
   - **Simple Semantic Search**: Find recipes based on natural language descriptions
   - **Filtered Search**: Combine semantic search with specific criteria like:
     - Cuisine type
     - Meal category
     - Diet restrictions
     - Maximum cooking time
     - Required/excluded ingredients

5. **Implementation**:
   - Terminal-based demo interface for testing
   - FastAPI implementation for web service deployment

## Key Advantages
- Understands natural language queries ("quick weeknight dinner", "something spicy with chicken")
- Discovers conceptually similar recipes even with different terminology
- Combines semantic understanding with practical filtering
- Scales efficiently to large recipe collections

This approach demonstrates how vector databases enable sophisticated information retrieval that understands meaning rather than just matching keywords.