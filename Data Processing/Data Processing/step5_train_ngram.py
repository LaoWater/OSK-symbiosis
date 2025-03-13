import json
from collections import defaultdict
import pickle

# Load the preprocessed diary data
with open(r'Data\preprocessed_diary.json', 'r') as f:
    preprocessed_data = json.load(f)

# Initialize a defaultdict for n-gram frequencies
n = 3  # Trigram model
ngram_model = defaultdict(lambda: defaultdict(int))

# Train the n-gram model
for paragraph in preprocessed_data:
    for i in range(len(paragraph) - n + 1):
        ngram = tuple(paragraph[i:i + n - 1])  # Previous n-1 words
        next_word = paragraph[i + n - 1]       # Next word
        ngram_model[ngram][next_word] += 1

# Convert counts to probabilities
for ngram in ngram_model:
    total_count = sum(ngram_model[ngram].values())
    for word in ngram_model[ngram]:
        ngram_model[ngram][word] /= total_count

# Save the n-gram model
with open(r'Models\ngram_model.pkl', 'wb') as f:
    pickle.dump(dict(ngram_model), f)  # Convert to dict for pickling

print("N-gram model trained and saved to 'ngram_model.pkl'")