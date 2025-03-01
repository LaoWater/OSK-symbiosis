import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


def fetch_hacker_news_headlines():
    """
    Scrape the front page of Hacker News and return a list of dictionaries containing the title and URL.
    """
    url = "https://news.ycombinator.com/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, 'html.parser')

    headlines = []
    # Each story title is contained in a <a> tag with class "storylink" or inside <span class="titleline">
    # The HTML structure may vary so adjust selectors as needed.
    for item in soup.select(".titleline"):
        a_tag = item.find("a")
        if a_tag:
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href")
            headlines.append({"title": title, "url": link})
    return headlines


def embed_texts(texts, model):
    """
    Compute vector embeddings for a list of texts using the provided model.
    """
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return embeddings


def build_faiss_index(embeddings):
    """
    Create a FAISS index from the computed embeddings.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index


def search_index(query, model, index, metadata, k=5):
    """
    Search the FAISS index with the query. Returns top-k matching headlines along with their URLs.
    """
    query_vec = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, k)

    print(f"\nSearch results for query: '{query}'")
    for dist, idx in zip(distances[0], indices[0]):
        # Guard against out-of-bound indices
        if idx < len(metadata):
            item = metadata[idx]
            print(f"Score: {dist:.4f} | Title: {item['title']} | URL: {item['url']}")
    print()


def main():
    print("Fetching Hacker News headlines...")
    headlines = fetch_hacker_news_headlines()
    if not headlines:
        print("No headlines fetched. Exiting.")
        return

    # Display fetched headlines
    print(f"Fetched {len(headlines)} headlines from Hacker News.\n")

    # Extract titles for embedding
    titles = [item['title'] for item in headlines]

    # Load the embedding model (using a small, efficient model for demonstration)
    print("Loading the embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Computing embeddings for headlines...")
    embeddings = embed_texts(titles, model)

    # Build the FAISS vector index
    print("Building the FAISS index...")
    index = build_faiss_index(embeddings)

    # Interactive search loop
    while True:
        query = input("Enter a search query (or type 'exit' to quit): ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        search_index(query, model, index, headlines, k=5)


if __name__ == "__main__":
    main()
