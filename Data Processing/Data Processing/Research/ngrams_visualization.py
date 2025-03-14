import pickle
import matplotlib.pyplot as plt

# Load the trigram model
with open(r'DeepSeek-R\ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)

# Select a bigram (ensure it exists in the model)
bigram = ("Good", "morning")
next_words = ngram_model.get(bigram, {})

if not next_words:
    print(f"Bigram {bigram} not found in the model. Please choose another.")
else:
    # Get top 5 next words sorted by probability
    sorted_words = sorted(next_words.items(), key=lambda x: x[1], reverse=True)[:5]
    words, probs = zip(*sorted_words)

    # Create bar chart
    plt.figure(figsize=(8, 4))
    plt.bar(words, probs, color='skyblue')
    plt.xlabel('Next Word')
    plt.ylabel('Probability')
    plt.title(f'Next Word Probabilities for Bigram {bigram}')
    plt.tight_layout()
    plt.savefig('ngram_visualization.png', dpi=300)
    plt.show()