import pickle
import matplotlib.pyplot as plt

# Load the trained n-gram model
with open(r'Models\ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)

# 1. Print some sample n-grams
print("Sample n-grams from the model:")
for ngram, next_words in list(ngram_model.items())[:10]:  # Show first 10 entries
    print(f"{ngram} -> {dict(next_words)}")

# 2. Graph the most common predictions for a chosen n-gram
sample_ngram = ('i', 'want')  # Modify this to test different word pairs

if sample_ngram in ngram_model:
    words, probs = zip(*ngram_model[sample_ngram].items())

    plt.figure(figsize=(10, 5))
    plt.bar(words, probs, color='skyblue')
    plt.xlabel("Next Word")
    plt.ylabel("Probability")
    plt.title(f"Next Word Predictions for {sample_ngram}")
    plt.xticks(rotation=45)
    plt.show()
else:
    print(f"N-gram {sample_ngram} not found in model.")

# 3. Check model size & most common n-grams
print(f"\nTotal unique n-grams: {len(ngram_model)}")

# Find most common n-grams
most_common_ngrams = sorted(ngram_model.items(), key=lambda x: sum(x[1].values()), reverse=True)[:30]

print("\nMost common n-grams and their next word distributions:")
for ngram, next_words in most_common_ngrams:
    print(f"{ngram} -> {dict(next_words)}")
