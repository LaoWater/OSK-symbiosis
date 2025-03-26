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





def run_tests():
    """
    Run multiple test cases to validate both word completion and next word prediction.
    """
    test_cases = [
        # Word Completion Tests
        (["hello"], "worl"),  # Should suggest "world"
        (["good"], "mor"),  # Should suggest "morning"
        ([], "com"),  # Should suggest common words starting with "com"
        (["the", "quick"], "bro"),  # Should suggest "brown"
        (["I", "am"], "hap"),  # Should suggest "happy"
        (["let's", "go"], "par"),  # Should suggest "party" or "park"
        (["I", "like"], "cho"),  # Should suggest "chocolate"
        (["this", "is"], "imp"),  # Should suggest "important"
        (["she", "loves"], "flo"),  # Should suggest "flowers"
        ([], "rea"),  # Should suggest common words like "read", "real", "reason"

        # Next Word Prediction Tests - Some issues here - losing words?
        (["hello", "how"], ""),  # Should suggest "are", "is", "do", etc.
        (["good", "morning"], ""),  # Should suggest common words like "everyone", "to"
        (["I", "am"], ""),  # Should suggest "happy", "fine", "tired"
        (["let's", "go"], ""),  # Should suggest "to", "out", "for"
        (["the", "weather"], ""),  # Should suggest "is", "today", "looks"
        (["she", "is"], ""),  # Should suggest "beautiful", "happy", "smart"
        (["he", "wants"], ""),  # Should suggest "to", "a", "something"
        (["I", "love"], ""),  # Should suggest "you", "coding", "music"
        (["they", "are"], ""),  # Should suggest "coming", "here", "happy"
        (["we", "should"], ""),  # Should suggest "go", "try", "see"
    ]

    print("\nRunning tests...\n")

    for i, (context, prefix) in enumerate(test_cases):
        if prefix:  # Test word completion
            result = complete_current_word(prefix, context, top_k=3)
            print(f"Test {i+1}: complete_current_word('{prefix}', {context}) → {result}")
        else:  # Test next word prediction
            result = predict_next_word(context, top_k=5)
            print(f"Test {i+1}: predict_next_word({context}) → {result}")

    print("\nTesting completed.")

if __name__ == "__main__":
    run_tests()