import os
import json
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Tuple, Any
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn
from tqdm import tqdm

# Load environment variables
load_dotenv()


class RecipeSearchEngine:
    def __init__(self, data_path=None):
        # Initialize the sentence transformer model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize FAISS index to None (will be created later)
        self.index = None

        # Store for our recipe data
        self.recipes = []

        # If data is provided, load it
        if data_path:
            self.load_data(data_path)
        else:
            # Otherwise, fetch from API
            self.fetch_recipes_from_api()

        # Build the vector index
        self.build_index()

    def fetch_recipes_from_api(self, limit=1000):
        """Fetch recipes from Spoonacular API or similar"""
        print("Fetching recipes from API...")

        # In a real implementation, you would use your API key:
        # api_key = os.getenv("SPOONACULAR_API_KEY")

        # For demonstration, we'll use a sample dataset
        # This simulates what we'd get from an API
        sample_recipes = []

        # Let's create some sample recipe data (in real app, this would come from API)
        cuisines = ["Italian", "Mexican", "Indian", "Chinese", "American", "Japanese", "Thai", "French"]
        meal_types = ["breakfast", "lunch", "dinner", "snack", "dessert"]
        diets = ["vegetarian", "vegan", "gluten-free", "keto", "paleo"]

        # Common ingredients by cuisine
        cuisine_ingredients = {
            "Italian": ["pasta", "tomato", "basil", "olive oil", "garlic", "parmesan"],
            "Mexican": ["tortilla", "beans", "avocado", "corn", "cilantro", "lime"],
            "Indian": ["rice", "lentils", "curry powder", "garam masala", "ghee", "chickpeas"],
            "Chinese": ["soy sauce", "rice", "ginger", "scallion", "sesame oil", "tofu"],
            "American": ["beef", "cheese", "potato", "butter", "corn", "bacon"],
            "Japanese": ["rice", "nori", "soy sauce", "mirin", "wasabi", "fish"],
            "Thai": ["coconut milk", "lime", "fish sauce", "lemongrass", "chili", "rice noodles"],
            "French": ["butter", "cream", "wine", "herbs", "cheese", "baguette"]
        }

        for i in range(limit):
            cuisine = np.random.choice(cuisines)
            meal_type = np.random.choice(meal_types)

            # Generate a random recipe with ingredients common to the cuisine
            num_ingredients = np.random.randint(3, 10)
            base_ingredients = cuisine_ingredients[cuisine]
            ingredients = np.random.choice(base_ingredients, min(num_ingredients, len(base_ingredients)),
                                           replace=False).tolist()

            # Add some random diet labels
            has_diet = np.random.random() > 0.7
            diet_labels = []
            if has_diet:
                num_diets = np.random.randint(1, 3)
                diet_labels = np.random.choice(diets, num_diets, replace=False).tolist()

            cooking_time = np.random.randint(10, 120)

            recipe = {
                "id": i,
                "title": f"{cuisine} {meal_type.capitalize()} Recipe #{i}",
                "cuisine": cuisine,
                "meal_type": meal_type,
                "ingredients": ingredients,
                "diet_labels": diet_labels,
                "cooking_time_minutes": cooking_time,
                "instructions": f"Sample instructions for {cuisine} {meal_type} recipe #{i}",
                "difficulty": np.random.choice(["easy", "medium", "hard"])
            }

            sample_recipes.append(recipe)

        self.recipes = sample_recipes
        print(f"Generated {len(sample_recipes)} sample recipes.")

    def load_data(self, data_path):
        """Load recipe data from a JSON file"""
        with open(data_path, 'r') as f:
            self.recipes = json.load(f)
        print(f"Loaded {len(self.recipes)} recipes from {data_path}")

    def save_data(self, output_path):
        """Save the current recipe data to a JSON file"""
        with open(output_path, 'w') as f:
            json.dump(self.recipes, f, indent=2)
        print(f"Saved {len(self.recipes)} recipes to {output_path}")

    def create_recipe_embeddings(self) -> np.ndarray:
        """Create vector embeddings for all recipes"""
        print("Creating recipe embeddings...")

        # Create rich text descriptions for each recipe to embed
        descriptions = []
        for recipe in self.recipes:
            description = f"{recipe['title']}. {recipe['cuisine']} {recipe['meal_type']} with " + \
                          f"{', '.join(recipe['ingredients'])}. " + \
                          f"Diet types: {', '.join(recipe['diet_labels']) if recipe['diet_labels'] else 'none'}. " + \
                          f"Cooking time: {recipe['cooking_time_minutes']} minutes. " + \
                          f"Difficulty: {recipe['difficulty']}."
            descriptions.append(description)

        # Create embeddings
        embeddings = self.model.encode(descriptions, show_progress_bar=True)
        return embeddings

    def build_index(self):
        """Build the FAISS index from recipe embeddings"""
        # Create embeddings for recipes
        embeddings = self.create_recipe_embeddings()

        # Get the dimensionality of the embeddings
        d = embeddings.shape[1]

        # Create a FAISS index
        self.index = faiss.IndexFlatL2(d)

        # Add the recipe embeddings to the index
        self.index.add(embeddings.astype('float32'))

        print(f"Built FAISS index with {self.index.ntotal} recipes")

    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for recipes similar to the query"""
        # Create embedding for the query
        query_embedding = self.model.encode([query])

        # Search the FAISS index
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        # Get the recipes for the indices
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.recipes):  # Safety check
                recipe = self.recipes[idx].copy()
                recipe['search_score'] = float(distances[0][i])
                results.append(recipe)

        return results

    def filter_search(self,
                      query: str = None,
                      cuisine: str = None,
                      meal_type: str = None,
                      diet: str = None,
                      max_cooking_time: int = None,
                      include_ingredients: List[str] = None,
                      exclude_ingredients: List[str] = None,
                      k: int = 10) -> List[Dict]:
        """
        Advanced search with filtering.
        If query is None, just apply the filters.
        """
        if query:
            # Get initial semantic search results (get more than needed to allow filtering)
            initial_results = self.search(query, k=min(100, len(self.recipes)))
        else:
            # If no query, start with all recipes
            initial_results = self.recipes

        # Apply filters
        filtered_results = []
        for recipe in initial_results:
            # Check all filter conditions
            if cuisine and recipe['cuisine'] != cuisine:
                continue

            if meal_type and recipe['meal_type'] != meal_type:
                continue

            if diet and diet not in recipe['diet_labels']:
                continue

            if max_cooking_time and recipe['cooking_time_minutes'] > max_cooking_time:
                continue

            if include_ingredients:
                if not all(ing.lower() in [i.lower() for i in recipe['ingredients']] for ing in include_ingredients):
                    continue

            if exclude_ingredients:
                if any(ing.lower() in [i.lower() for i in recipe['ingredients']] for ing in exclude_ingredients):
                    continue

            filtered_results.append(recipe)

            # Only take top k after filtering
            if len(filtered_results) >= k:
                break

        return filtered_results[:k]


# Create FastAPI app
app = FastAPI(title="Semantic Recipe Search API")


class SearchQuery(BaseModel):
    query: str = None
    cuisine: str = None
    meal_type: str = None
    diet: str = None
    max_cooking_time: int = None
    include_ingredients: List[str] = None
    exclude_ingredients: List[str] = None
    k: int = 10


@app.get("/")
def read_root():
    return {"message": "Welcome to the Semantic Recipe Search API"}


@app.post("/search")
def search_recipes(params: SearchQuery):
    results = search_engine.filter_search(
        query=params.query,
        cuisine=params.cuisine,
        meal_type=params.meal_type,
        diet=params.diet,
        max_cooking_time=params.max_cooking_time,
        include_ingredients=params.include_ingredients,
        exclude_ingredients=params.exclude_ingredients,
        k=params.k
    )
    return {"results": results}


@app.get("/cuisines")
def get_cuisines():
    cuisines = set(recipe["cuisine"] for recipe in search_engine.recipes)
    return {"cuisines": list(cuisines)}


@app.get("/meal-types")
def get_meal_types():
    meal_types = set(recipe["meal_type"] for recipe in search_engine.recipes)
    return {"meal_types": list(meal_types)}


@app.get("/diet-labels")
def get_diet_labels():
    all_diets = set()
    for recipe in search_engine.recipes:
        all_diets.update(recipe["diet_labels"])
    return {"diet_labels": list(all_diets)}


# Initialize search engine with sample data
search_engine = RecipeSearchEngine()


# Demo function for terminal testing
def demo():
    print("\n===== SEMANTIC RECIPE SEARCH DEMO =====\n")

    while True:
        print("\nOptions:")
        print("1. Simple semantic search")
        print("2. Advanced filtered search")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            query = input("\nEnter your recipe search query: ")
            results = search_engine.search(query, k=5)

            print(f"\nTop 5 results for '{query}':")
            for i, result in enumerate(results):
                print(f"\n{i + 1}. {result['title']}")
                print(f"   Cuisine: {result['cuisine']}, Type: {result['meal_type']}")
                print(f"   Ingredients: {', '.join(result['ingredients'])}")
                print(f"   Diet labels: {', '.join(result['diet_labels']) if result['diet_labels'] else 'none'}")
                print(f"   Cooking time: {result['cooking_time_minutes']} minutes")
                print(f"   Difficulty: {result['difficulty']}")
                print(f"   Similarity score: {result['search_score']:.4f}")

        elif choice == "2":
            query = input("\nEnter search query (or leave empty): ")
            if query.strip() == "":
                query = None

            cuisine = input("Filter by cuisine (or leave empty): ")
            if cuisine.strip() == "":
                cuisine = None

            meal_type = input("Filter by meal type (or leave empty): ")
            if meal_type.strip() == "":
                meal_type = None

            diet = input("Filter by diet (or leave empty): ")
            if diet.strip() == "":
                diet = None

            max_time_str = input("Maximum cooking time in minutes (or leave empty): ")
            max_cooking_time = int(max_time_str) if max_time_str.strip() and max_time_str.isdigit() else None

            include_str = input("Ingredients to include (comma-separated, or leave empty): ")
            include_ingredients = [i.strip() for i in include_str.split(',')] if include_str.strip() else None

            exclude_str = input("Ingredients to exclude (comma-separated, or leave empty): ")
            exclude_ingredients = [i.strip() for i in exclude_str.split(',')] if exclude_str.strip() else None

            results = search_engine.filter_search(
                query=query,
                cuisine=cuisine,
                meal_type=meal_type,
                diet=diet,
                max_cooking_time=max_cooking_time,
                include_ingredients=include_ingredients,
                exclude_ingredients=exclude_ingredients,
                k=5
            )

            print(f"\nTop 5 results for advanced search:")
            if not results:
                print("No recipes found matching your criteria.")

            for i, result in enumerate(results):
                print(f"\n{i + 1}. {result['title']}")
                print(f"   Cuisine: {result['cuisine']}, Type: {result['meal_type']}")
                print(f"   Ingredients: {', '.join(result['ingredients'])}")
                print(f"   Diet labels: {', '.join(result['diet_labels']) if result['diet_labels'] else 'none'}")
                print(f"   Cooking time: {result['cooking_time_minutes']} minutes")
                print(f"   Difficulty: {result['difficulty']}")
                if 'search_score' in result:
                    print(f"   Similarity score: {result['search_score']:.4f}")

        elif choice == "3":
            print("\nThank you for using Semantic Recipe Search!")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


# Run the API if the script is executed directly
if __name__ == "__main__":
    # Uncomment to run the demo in terminal:
    # demo()

    # Uncomment to run the API server:
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    # For this example, run the demo
    demo()