import json
import pygtrie as trie
import pickle

# Load the vocabulary
with open('vocabulary.json', 'r') as f:
    vocabulary = json.load(f)

# Initialize the trie
word_trie = trie.CharTrie()

# Insert each word into the trie
for word in vocabulary:
    word_trie[word] = True  # We store True as a placeholder; could store frequency if needed

# Save the trie for later use
with open('word_trie.pkl', 'wb') as f:
    pickle.dump(word_trie, f)

print("Trie built and saved to 'word_trie.pkl'")