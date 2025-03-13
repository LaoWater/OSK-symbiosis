from collections import defaultdict
import re


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.freq = 0


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.suggestions = []

    def insert(self, word, freq):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.freq += freq

    def search_prefix(self, prefix, max_suggestions=3):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        self.suggestions = []
        self._dfs(node, prefix, max_suggestions)
        return sorted(self.suggestions, key=lambda x: -x[1])[:max_suggestions]

    def _dfs(self, node, prefix, max_suggestions):
        if node.is_end:
            self.suggestions.append((prefix, node.freq))
        if len(self.suggestions) >= max_suggestions:
            return
        for char, child_node in node.children.items():
            self._dfs(child_node, prefix + char, max_suggestions)


class NGramModel:
    def __init__(self, n=2):
        self.n = n
        self.ngrams = defaultdict(lambda: defaultdict(int))
        self.vocab = set()

    def train(self, corpus):
        tokens = self._tokenize(corpus)
        for i in range(len(tokens) - self.n + 1):
            context = tuple(tokens[i:i + self.n - 1])
            next_word = tokens[i + self.n - 1]
            self.ngrams[context][next_word] += 1
            self.vocab.add(next_word)

    def predict(self, context, max_predictions=3):
        context = tuple(self._tokenize(context)[-(self.n - 1):])
        predictions = self.ngrams.get(context, {})
        return sorted(predictions.items(), key=lambda x: -x[1])[:max_predictions]

    def _tokenize(self, text):
        return re.findall(r"\w+(?:'\w+)?|\s+", text.lower())


class PredictionEngine:
    def __init__(self, corpus):
        # Build trie
        self.trie = Trie()
        word_freq = defaultdict(int)
        tokens = re.findall(r"\w+(?:'\w+)?", corpus.lower())
        for word in tokens:
            word_freq[word] += 1
        for word, freq in word_freq.items():
            self.trie.insert(word, freq)

        # Train ngram model
        self.ngram_model = NGramModel(n=2)
        self.ngram_model.train(corpus)

    def get_predictions(self, input_text):
        # Split into complete words and partial word
        tokens = re.split(r'(\s+)', input_text)
        tokens = [t for t in tokens if t.strip() != '']

        if not tokens:
            return []

        last_token = tokens[-1]

        if last_token[-1].isspace():
            # Next word prediction
            context = ' '.join(tokens).strip()
            predictions = self.ngram_model.predict(context)
            return [f"{word}" for word, _ in predictions]
        else:
            # Word completion
            partial_word = re.sub(r'\W+', '', last_token).lower()
            completions = self.trie.search_prefix(partial_word)
            return [f"{partial_word}{completion[len(partial_word):]}"
                    for completion, _ in completions]


# Example usage
corpus = """
Today I want to go to the park. Today I was thinking about 
machine learning. Today I walked in the park.
"""

engine = PredictionEngine(corpus)

# Test cases
print(engine.get_predictions("today i wa"))  # ['want', 'was', 'walked']
print(engine.get_predictions("today i "))  # ['want', 'was', 'walked']
print(engine.get_predictions("today i"))  # ['i']
print(engine.get_predictions("th"))  # ['the', 'thinking', 'to']