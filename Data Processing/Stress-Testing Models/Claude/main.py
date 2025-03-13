import pickle
import re
from collections import Counter, defaultdict


class WordPredictor:
    def __init__(self):
        # N-gram storage
        self.unigrams = Counter()
        self.bigrams = defaultdict(Counter)
        self.trigrams = defaultdict(lambda: defaultdict(Counter))

        # Word completion storage
        self.word_prefixes = defaultdict(Counter)

        # Cache for frequent queries
        self.prediction_cache = {}
        self.max_cache_size = 10000

    def train(self, paragraphs):
        """Train the model on paragraphs of text."""
        # Clean and tokenize the text
        tokens = []
        for paragraph in paragraphs:
            # Normalize text
            text = paragraph.lower()
            # Split into words
            words = re.findall(r'\b\w+\b|[^\w\s]', text)
            tokens.extend(words)

            # Build word prefixes for completion
            for word in words:
                for i in range(1, len(word)):
                    prefix = word[:i]
                    self.word_prefixes[prefix][word] += 1

            # Build n-grams
            self.unigrams.update(words)

            # Build bigrams
            for i in range(len(words) - 1):
                self.bigrams[words[i]][words[i + 1]] += 1

            # Build trigrams
            for i in range(len(words) - 2):
                self.trigrams[words[i]][words[i + 1]][words[i + 2]] += 1

    def predict_completion(self, partial_word, max_suggestions=3):
        """Predict completions for a partial word."""
        if not partial_word:
            return []

        # Check cache first
        cache_key = f"completion:{partial_word}"
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]

        # Get all possible completions
        completions = self.word_prefixes[partial_word].most_common(max_suggestions)

        # If we don't have enough completions, try to find words starting with this prefix
        if len(completions) < max_suggestions:
            for word, count in self.unigrams.items():
                if word.startswith(partial_word) and word not in [c[0] for c in completions]:
                    completions.append((word, count))
                    if len(completions) >= max_suggestions:
                        break

        result = [word for word, _ in completions[:max_suggestions]]

        # Update cache
        self._update_cache(cache_key, result)
        return result

    def predict_next_word(self, context, max_suggestions=3):
        """Predict the next word based on context."""
        if not context:
            return [word for word, _ in self.unigrams.most_common(max_suggestions)]

        # Check cache first
        cache_key = f"next:{context}"
        if cache_key in self.prediction_cache:
            return self.prediction_cache[cache_key]

        words = context.lower().split()

        # Use trigram if available
        if len(words) >= 2:
            last_two = words[-2:]
            if last_two[0] in self.trigrams and last_two[1] in self.trigrams[last_two[0]]:
                predictions = self.trigrams[last_two[0]][last_two[1]].most_common(max_suggestions)
                if predictions:
                    result = [word for word, _ in predictions]
                    self._update_cache(cache_key, result)
                    return result

        # Fallback to bigram
        if words:
            last_word = words[-1]
            if last_word in self.bigrams:
                predictions = self.bigrams[last_word].most_common(max_suggestions)
                if predictions:
                    result = [word for word, _ in predictions]
                    self._update_cache(cache_key, result)
                    return result

        # Fallback to most common words
        result = [word for word, _ in self.unigrams.most_common(max_suggestions)]
        self._update_cache(cache_key, result)
        return result

    def predict(self, current_text, max_suggestions=3):
        """Main prediction function for the keyboard."""
        if not current_text:
            return self.predict_next_word("", max_suggestions)

        # Split into words
        words = current_text.split()

        # If the text ends with a space, predict the next word
        if current_text.endswith(" "):
            return self.predict_next_word(current_text.strip(), max_suggestions)

        # Otherwise, predict word completion for the last partial word
        context = " ".join(words[:-1])
        partial_word = words[-1] if words else ""

        completions = self.predict_completion(partial_word, max_suggestions)

        # If we couldn't find completions, predict the next word
        if not completions and context:
            return [partial_word + " " + next_word for next_word in self.predict_next_word(context, max_suggestions)]

        return completions

    def _update_cache(self, key, value):
        """Update the prediction cache."""
        self.prediction_cache[key] = value

        # Remove oldest entries if cache is too large
        if len(self.prediction_cache) > self.max_cache_size:
            # Remove 10% of oldest entries
            keys_to_remove = list(self.prediction_cache.keys())[:self.max_cache_size // 10]
            for k in keys_to_remove:
                del self.prediction_cache[k]

    def save(self, filename):
        """Save the model to a file."""
        with open(filename, 'wb') as f:
            pickle.dump({
                'unigrams': self.unigrams,
                'bigrams': dict(self.bigrams),
                'trigrams': {k1: dict(v1) for k1, v1 in self.trigrams.items()},
                'word_prefixes': dict(self.word_prefixes)
            }, f)

    @classmethod
    def load(cls, filename):
        """Load the model from a file."""
        model = cls()
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            model.unigrams = data['unigrams']

            # Convert bigrams back to defaultdict
            model.bigrams = defaultdict(Counter)
            for k, v in data['bigrams'].items():
                model.bigrams[k] = v

            # Convert trigrams back to nested defaultdict
            model.trigrams = defaultdict(lambda: defaultdict(Counter))
            for k1, v1 in data['trigrams'].items():
                for k2, v2 in v1.items():
                    model.trigrams[k1][k2] = v2

            # Convert word prefixes back to defaultdict
            model.word_prefixes = defaultdict(Counter)
            for k, v in data['word_prefixes'].items():
                model.word_prefixes[k] = v

        return model


# Example usage:
if __name__ == "__main__":
    # Sample training data
    paragraphs = [
        "Today I went to the park. The weather was beautiful and sunny.",
        "I enjoy writing in my diary every day. It helps me reflect on my thoughts.",
        "The changing fortunes of time have taught me patience and resilience.",
        "Tomorrow I plan to visit my friend. We will go to the cinema."
    ]

    # Create and train the model
    predictor = WordPredictor()
    predictor.train(paragraphs)

    # Test some predictions
    test_inputs = [
        "Today I",
        "t",
        "in the changing fortunes of",
        "I enjoy w",
        ""
    ]

    for input_text in test_inputs:
        predictions = predictor.predict(input_text)
        print(f"Input: '{input_text}'")
        print(f"Predictions: {predictions}")
        print()

    # Save the model
    predictor.save("word_predictor.pkl")

    # Load the model
    loaded_predictor = WordPredictor.load("word_predictor.pkl")
    print("Model successfully saved and loaded!")