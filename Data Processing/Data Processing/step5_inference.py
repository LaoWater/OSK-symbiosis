# Where Context Happens: Inference Example
#
#
#
#



import pickle
import pygtrie as trie

# Load the trie and n-gram model
with open(r'Models\word_trie.pkl', 'rb') as f:
    word_trie = pickle.load(f)

with open(r'Models\ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)


# Function to get word completions with context
def get_completions(prefix, context, top_k=3):
    print(f"\nPrefix typed: '{prefix}'")
    print(f"Context (previous words): {context}")

    # Get all possible completions from the trie
    completions = [word for word in word_trie.iterkeys(prefix) if word.startswith(prefix)]
    print(f"Trie completions for '{prefix}': {completions[:5]}... (total: {len(completions)})")

    if not context:
        # No context: rank by frequency from the trie
        print("No context given. Ranking by frequency alone.")
        ranked = sorted(completions, key=lambda w: word_trie[w], reverse=True)[:top_k]
        print(f"Top {top_k} suggestions: {ranked}")
        return ranked

    # Use context with n-gram model (e.g., trigram)
    n = 3  # Trigram example
    ngram = tuple(context[-(n - 1):]) if len(context) >= n - 1 else tuple(context)
    print(f"Using n-gram context: {ngram}")

    # Score completions based on n-gram probabilities
    scores = {}
    for comp in completions:
        prob = ngram_model.get(ngram, {}).get(comp, 0)  # Probability of word given context
        scores[comp] = prob
        if prob > 0:
            print(f"Score for '{comp}' after '{ngram}': {prob}")

    # Rank by n-gram score, fallback to frequency if tied or no score
    ranked = sorted(completions, key=lambda w: (scores.get(w, 0), word_trie[w]), reverse=True)[:top_k]
    print(f"Top {top_k} suggestions with context: {ranked}")
    return ranked



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



print("\nRunning tests on context-considering behavior:")
# Test 1: With context
context = ["I", "was"]
prefix = "lo"
suggestions = get_completions(prefix, context)

# Test 2: Without context
context = []
prefix = "lo"
suggestions = get_completions(prefix, context)