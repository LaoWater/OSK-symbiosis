import pickle
import pygtrie as trie

# Load the pre-trained models
with open(r'Models\word_trie.pkl', 'rb') as f:
    word_trie = pickle.load(f)

with open(r'Models\ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)


def complete_current_word(prefix, context, top_k=3):
    """
    Suggest completions for the current word being typed.

    Args:
        prefix (str): The partial word being typed (e.g., "bea").
        context (list): List of previous words (e.g., ["so"]).
        top_k (int): Number of suggestions to return (default: 3).

    Returns:
        list: Top k completion suggestions (e.g., ["bear", "beach", "beat"]).
    """
    if not prefix:  # Return empty list if no prefix is provided
        return []

    # Get all possible completions from the trie
    completions = [word for word in word_trie.iterkeys(prefix) if word.startswith(prefix)]

    if not context:
        # No context: rank by frequency from the trie
        return sorted(completions, key=lambda w: word_trie[w], reverse=True)[:top_k]

    # Use context with n-gram model (trigram assumed)
    n = 3
    ngram = tuple(context[-(n - 1):]) if len(context) >= n - 1 else tuple(context)
    scores = {}
    for comp in completions:
        prob = ngram_model.get(ngram, {}).get(comp, 0)  # Probability given context
        scores[comp] = prob

    # Rank by n-gram probability, with frequency as tiebreaker
    return sorted(completions, key=lambda w: (scores.get(w, 0), word_trie[w]), reverse=True)[:top_k]


def predict_next_word(context, top_k=5):
    """
    Predict the next word based on previous words.

    Args:
        context (list): List of previous words (e.g., ["good", "morning"]).
        top_k (int): Number of suggestions to return (default: 5).

    Returns:
        list: Top k next word suggestions (e.g., ["to", "everyone", "sunshine"]).
    """
    n = 3  # Assuming trigram model
    ngram = tuple(context[-(n - 1):]) if len(context) >= n - 1 else tuple(context)
    if ngram in ngram_model:
        next_words = ngram_model[ngram]
        return sorted(next_words, key=next_words.get, reverse=True)[:top_k]
    return []  # Return empty list if no predictions available





def main():
    # Example test cases
    test_context_1 = ["so"]
    test_prefix_1 = "bea"

    test_context_2 = ["good", "morning"]
    test_prefix_2 = "sun"

    print("Completion suggestions:", complete_current_word(test_prefix_1, test_context_1, top_k=3))
    print("Completion suggestions:", complete_current_word(test_prefix_2, test_context_2, top_k=3))

    print("Next word predictions:", predict_next_word(test_context_1, top_k=5))
    print("Next word predictions:", predict_next_word(test_context_2, top_k=5))


if __name__ == "__main__":
    main()