import pickle
import pygtrie as trie

# Load the trie and n-gram model
with open(r'Models\word_trie.pkl', 'rb') as f:
    word_trie = pickle.load(f)

with open(r'Models\ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)


# Function to get word completions (current word prediction)
def get_completions(prefix, context, top_k=5):
    # Find all words in the trie starting with the prefix
    completions = [word for word in word_trie.iterkeys(prefix) if word.startswith(prefix)]

    if not completions:
        return []

    if not context:
        # No context: rank by frequency
        return sorted(completions, key=lambda w: word_trie[w], reverse=True)[:top_k]

    # Use n-gram model to rank based on context
    n = 3  # Assuming trigram model
    ngram = tuple(context[-(n - 1):]) if len(context) >= n - 1 else tuple(context)
    scores = {}
    for comp in completions:
        # Probability of completion given the n-gram context
        scores[comp] = ngram_model.get(ngram, {}).get(comp, 0)

    # Sort by n-gram probability, fallback to frequency
    return sorted(completions, key=lambda w: (scores.get(w, 0), word_trie[w]), reverse=True)[:top_k]


# Function to predict the next word
def get_next_words(context, top_k=5):
    n = 3  # Assuming trigram model
    ngram = tuple(context[-(n - 1):]) if len(context) >= n - 1 else tuple(context)
    if ngram in ngram_model:
        # Sort next words by probability
        next_words = ngram_model[ngram]
        return sorted(next_words, key=next_words.get, reverse=True)[:top_k]
    return []


# Main prediction function
def predict(current_text, top_k=5):
    words = current_text.strip().split()
    if current_text.endswith(" "):
        # Predict next word
        return get_next_words(words, top_k)
    else:
        # Complete current word
        prefix = words[-1] if words else current_text
        context = words[:-1]
        return get_completions(prefix, context, top_k)


# Test cases
test_cases = [
    "so bea",  # Current word completion with context
    "good morning ",  # Next word prediction
    "life sen",  # Current word completion with context
    "tran",  # Completion with no context
    " ",  # Next word with no context (edge case)
]

# Run tests
print("Running tests on trie and n-gram models:")
for test in test_cases:
    suggestions = predict(test)
    print(f"Input: '{test}' -> Suggestions: {suggestions}")