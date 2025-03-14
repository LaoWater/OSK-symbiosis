import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the n-gram model
with open(r'ngram_model.pkl', 'rb') as f:
    ngram_model = pickle.load(f)

# Find representative bigrams
max_entropy = -1
max_entropy_ngram = None
one_next_word_ngram = None
max_max_prob = -1
max_max_prob_ngram = None

# Iterate through all bigrams to select representatives
for ngram in ngram_model:
    probs = list(ngram_model[ngram].values())
    if len(probs) == 1:
        one_next_word_ngram = ngram  # Bigram with only one next word
        continue
    if len(probs) > 1:
        # Compute entropy: -sum(p * log(p))
        entropy = -sum(p * np.log(p) for p in probs)
        if entropy > max_entropy:
            max_entropy = entropy
            max_entropy_ngram = ngram  # Bigram with highest entropy
        max_prob = max(probs)
        if max_prob > max_max_prob:
            max_max_prob = max_prob
            max_max_prob_ngram = ngram  # Bigram with highest max probability


# Function to plot next words for a given bigram
def plot_next_words(ngram, ax, title):
    next_words = ngram_model[ngram]
    # Sort by probability and take top 5 (or all if less than 5)
    sorted_words = sorted(next_words.items(), key=lambda x: x[1], reverse=True)[:5]
    words, probs = zip(*sorted_words)
    ax.barh(words, probs, color='skyblue')
    ax.set_xlabel('Probability')
    ax.set_title(title, fontsize=10)
    ax.invert_yaxis()  # Highest probability at the top
    ax.set_xlim(0, 1.1)  # Extend x-axis for text labels
    # Add probability labels
    for i, (word, prob) in enumerate(sorted_words):
        ax.text(prob + 0.05, i, f"{prob:.2f}", va='center', fontsize=9)


# Set Seaborn style for better aesthetics
sns.set_style("whitegrid")

# Create figure with three subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot each scenario
plot_next_words(max_entropy_ngram, axes[0],
                f"High Uncertainty (Entropy: {max_entropy:.2f})\nBigram: {' '.join(max_entropy_ngram)}")
plot_next_words(one_next_word_ngram, axes[1],
                f"Complete Certainty\nBigram: {' '.join(one_next_word_ngram)}")
plot_next_words(max_max_prob_ngram, axes[2],
                f"High Certainty (Max Prob: {max_max_prob:.2f})\nBigram: {' '.join(max_max_prob_ngram)}")

# Adjust layout and save/display
plt.tight_layout()
plt.savefig('ngram_visualization.png')  # Save the figure
plt.show()
