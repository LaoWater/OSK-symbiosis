"""
WordPredictor Architecture:

1. **Trie for Word Completion**:
   - Stores vocabulary words for fast prefix lookups.
   - Enables efficient word completion suggestions.

2. **N-Gram Language Model**:
   - Uses an (n-1)-gram context to predict the next word.
   - Trains on text by counting occurrences of (n-1)-gram sequences.
   - Converts counts into probabilities for ranking predictions.

3. **Prediction Logic**:
   - If input ends with a space → Predict next word using the n-gram model.
   - If input is a partial word → Suggest completions from the trie.
   - If context exists → Rank suggestions using n-gram probabilities.

4. **Efficiency**:
   - Uses a **trie** for fast prefix search.
   - Uses a **default dictionary** for efficient probability storage.
   - Supports **top-k filtering** to limit output size.
"""

import nltk
from nltk.util import ngrams
from collections import defaultdict
import pygtrie as trie


class WordPredictor:
    def __init__(self, n=3, top_k=5):
        self.n = n  # Trigram model by default
        self.top_k = top_k
        self.trie = trie.CharTrie()  # For word completion
        self.ngram_model = defaultdict(lambda: defaultdict(int))  # For probabilities
        self.vocab = set()

    def train(self, text):
        """Train the trie and n-gram model on the diary text."""
        words = nltk.word_tokenize(text.lower())  # Lowercase for simplicity
        self.vocab.update(words)

        # Build trie
        for word in self.vocab:
            self.trie[word] = True  # Could store frequency here

        # Train n-gram model
        for i in range(len(words) - self.n + 1):
            ngram = tuple(words[i:i + self.n - 1])
            next_word = words[i + self.n - 1]
            self.ngram_model[ngram][next_word] += 1

        # Convert counts to probabilities
        for ngram in self.ngram_model:
            total = sum(self.ngram_model[ngram].values())
            for word in self.ngram_model[ngram]:
                self.ngram_model[ngram][word] /= total

    def get_completions(self, prefix, context):
        """Suggest completions for a partial word."""
        completions = [word for word in self.trie.iterkeys(prefix) if word.startswith(prefix)]
        if not completions:
            return []

        if not context:
            return completions[:self.top_k]  # No context, return top-k

        # Score completions with n-gram model
        scores = {}
        ngram = tuple(context[-(self.n - 1):]) if len(context) >= self.n - 1 else tuple(context)
        for comp in completions:
            scores[comp] = self.ngram_model[ngram].get(comp, 0)  # Default to 0 if unseen

        return sorted(scores, key=scores.get, reverse=True)[:self.top_k]

    def get_next_words(self, context):
        """Predict the next word after a space."""
        ngram = tuple(context[-(self.n - 1):]) if len(context) >= self.n - 1 else tuple(context)
        if ngram in self.ngram_model:
            return sorted(self.ngram_model[ngram], key=self.ngram_model[ngram].get, reverse=True)[:self.top_k]
        return []  # Could implement backoff here

    def predict(self, current_text):
        """Main prediction function."""
        words = current_text.split()
        if current_text.endswith(" "):
            return self.get_next_words(words)
        else:
            prefix = words[-1] if words else current_text
            context = words[:-1]
            return self.get_completions(prefix, context)


# Example usage
diary_text = "today i was feeling great in the changing fortunes of time i found peace"
predictor = WordPredictor(n=3, top_k=5)
predictor.train(diary_text)

print(predictor.predict("today i wa"))  # e.g., ['was']
print(predictor.predict("in the changing fortunes of "))  # e.g., ['time']
print(predictor.predict("t"))  # e.g., ['today', 'the', 'time']
