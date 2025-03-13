# Context is not considered here. This code focuses entirely on creating a structure that stores individual words and their frequencies from your diary data.
# The trie is designed to help with prefix-based word completions—like suggesting "beautiful" or "beast"
# when you type "bea"—but it doesn’t know anything about how words relate to each other in sentences (e.g., "good morning" being followed by "my").
# That’s where context comes in, and it’s handled later, during Inference, not in the trie-building step.


import json
import pygtrie as trie
import pickle
from collections import Counter

# Load preprocessed diary data
with open(r'Data\preprocessed_diary.json', 'r') as f:
    preprocessed_data = json.load(f)

# Flatten into a list of words
all_words = [word for paragraph in preprocessed_data for word in paragraph]
print("Total words in diary:", len(all_words))
print("First 10 words:", all_words[:10])

# Count word frequencies
word_freq = Counter(all_words)
print("\nVocabulary size (unique words):", len(word_freq))
print("Top 10 most frequent words:")
for word, freq in word_freq.most_common(10):
    print(f"Word: '{word}', Frequency: {freq}")

# Initialize the trie
word_trie = trie.CharTrie()

# Insert words with their frequencies
for word, freq in word_freq.items():
    word_trie[word] = freq
    if len(word_trie) <= 25:  # Print first 25 insertions as an example
        print(f"Inserted into trie: '{word}' with frequency {freq}")

# Save the trie for later use
with open(r'Models\word_trie.pkl', 'wb') as f:
    pickle.dump(word_trie, f)

print("\nTrie built and saved to 'word_trie.pkl'")
print("Total words in trie:", len(word_trie))