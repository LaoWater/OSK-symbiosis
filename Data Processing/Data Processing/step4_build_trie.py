import json
import pygtrie as trie
import pickle
from collections import Counter

# Load preprocessed diary data
with open(r'Data\preprocessed_diary.json', 'r') as f:
    preprocessed_data = json.load(f)

# Flatten into a list of words
all_words = [word for paragraph in preprocessed_data for word in paragraph]

# Count word frequencies
word_freq = Counter(all_words)

# Initialize the trie
word_trie = trie.CharTrie()

# Insert words with their frequencies
for word, freq in word_freq.items():
    word_trie[word] = freq

# Save the trie for later use
with open(r'Models\word_trie.pkl', 'wb') as f:
    pickle.dump(word_trie, f)

print("Trie built and saved to 'word_trie.pkl'")