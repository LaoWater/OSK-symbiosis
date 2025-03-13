# Word Prediction System
#
# Architecture overview:
# - N-gram based language model (unigrams, bigrams, trigrams)
# - Word completion model using prefix-based prediction
# - Two primary prediction modes:
#   1. Next word prediction: Uses context to suggest complete words
#   2. Word completion: Completes partial words based on prefix
# - Combined prediction mode that weights both context and partial word
# - Dataset preparation for both transformer models and n-gram statistics
# - Simple backoff strategy from trigram -> bigram -> unigram for sparse data
#
# The system preprocesses text, builds statistical models, and provides
# interactive prediction capabilities with probability scores.

import re
import nltk
import random
from tqdm import tqdm

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def clean_text(text):
    """Basic text cleaning."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Normalize punctuation
    # Replace curly quotes with straight quotes
    text = text.replace('"', '"').replace('"', '"').replace('"', '"')
    text = text.replace("'", "'").replace("'", "'").replace("'", "'")
    return text


def prepare_diary_dataset(paragraphs, context_size=5, min_word_length=3):
    """
    Prepare a dataset for word prediction from paragraphs.

    Args:
        paragraphs: List of text paragraphs
        context_size: Number of preceding words to use as context
        min_word_length: Minimum word length for word completion tasks

    Returns:
        completion_samples: List of (context, partial_word, full_word) tuples
        next_word_samples: List of (context, next_word) tuples
    """
    completion_samples = []
    next_word_samples = []

    # Process each paragraph
    for paragraph in tqdm(paragraphs, desc="Processing paragraphs"):
        # Clean paragraph text
        paragraph = clean_text(paragraph)

        # Split paragraph into sentences
        sentences = nltk.sent_tokenize(paragraph)

        for sentence in sentences:
            # Tokenize sentence into words
            words = nltk.word_tokenize(sentence)

            # Create next word prediction samples
            for i in range(1, len(words)):
                # Get preceding context (up to context_size words)
                start_idx = max(0, i - context_size)
                context = ' '.join(words[start_idx:i])
                next_word = words[i]

                # Add sample
                next_word_samples.append((context, next_word))

            # Create word completion samples
            for i, word in enumerate(words):
                # Only consider words longer than min_word_length
                if len(word) > min_word_length:
                    # Get preceding context
                    start_idx = max(0, i - context_size)
                    context = ' '.join(words[start_idx:i])

                    # Create partial words of different lengths
                    for j in range(1, len(word)):
                        partial_word = word[:j]
                        full_word = word

                        # Add sample
                        completion_samples.append((context, partial_word, full_word))

    return completion_samples, next_word_samples


def create_transformer_datasets(completion_samples, next_word_samples, val_split=0.1):
    """
    Create training and validation datasets for a transformer model.

    Args:
        completion_samples: List of (context, partial_word, full_word) tuples
        next_word_samples: List of (context, next_word) tuples
        val_split: Proportion of data to use for validation

    Returns:
        train_completion, val_completion, train_next_word, val_next_word
    """
    # Shuffle samples
    random.shuffle(completion_samples)
    random.shuffle(next_word_samples)

    # Split into training and validation
    val_completion_size = int(len(completion_samples) * val_split)
    val_next_word_size = int(len(next_word_samples) * val_split)

    train_completion = completion_samples[val_completion_size:]
    val_completion = completion_samples[:val_completion_size]

    train_next_word = next_word_samples[val_next_word_size:]
    val_next_word = next_word_samples[:val_next_word_size]

    return train_completion, val_completion, train_next_word, val_next_word


def create_ngram_dataset(paragraphs):
    """
    Create n-gram counts from paragraphs.

    Args:
        paragraphs: List of text paragraphs

    Returns:
        unigrams, bigrams, trigrams, word_prefixes
    """
    from collections import Counter, defaultdict

    unigrams = Counter()
    bigrams = defaultdict(Counter)
    trigrams = defaultdict(lambda: defaultdict(Counter))
    word_prefixes = defaultdict(Counter)

    # Process each paragraph
    for paragraph in tqdm(paragraphs, desc="Building n-grams"):
        # Clean paragraph text
        paragraph = clean_text(paragraph)

        # Split paragraph into sentences
        sentences = nltk.sent_tokenize(paragraph)

        for sentence in sentences:
            # Tokenize sentence into words
            words = nltk.word_tokenize(sentence.lower())

            # Build unigrams
            unigrams.update(words)

            # Build word prefixes for completion
            for word in words:
                for i in range(1, len(word)):
                    prefix = word[:i]
                    word_prefixes[prefix][word] += 1

            # Build bigrams
            for i in range(len(words) - 1):
                bigrams[words[i]][words[i + 1]] += 1

            # Build trigrams
            for i in range(len(words) - 2):
                trigrams[words[i]][words[i + 1]][words[i + 2]] += 1

    return unigrams, bigrams, trigrams, word_prefixes


def save_datasets(train_completion, val_completion, train_next_word, val_next_word, output_dir):
    """Save datasets to files."""
    import os
    import json

    os.makedirs(output_dir, exist_ok=True)

    # Function to write samples to file
    def write_samples(samples, filename):
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')

    # Save completion datasets
    write_samples(train_completion, 'train_completion.jsonl')
    write_samples(val_completion, 'val_completion.jsonl')

    # Save next word datasets
    write_samples(train_next_word, 'train_next_word.jsonl')
    write_samples(val_next_word, 'val_next_word.jsonl')


def save_ngram_model(unigrams, bigrams, trigrams, word_prefixes, output_path):
    """Save n-gram model to a file."""
    import pickle

    # Convert nested defaultdicts to regular dicts for serialization
    bigrams_dict = {k: dict(v) for k, v in bigrams.items()}
    trigrams_dict = {k1: {k2: dict(v2) for k2, v2 in v1.items()}
                     for k1, v1 in trigrams.items()}
    word_prefixes_dict = {k: dict(v) for k, v in word_prefixes.items()}

    model_data = {
        'unigrams': unigrams,
        'bigrams': bigrams_dict,
        'trigrams': trigrams_dict,
        'word_prefixes': word_prefixes_dict
    }

    with open(output_path, 'wb') as f:
        pickle.dump(model_data, f)


def analyze_dataset(completion_samples, next_word_samples):
    """Print statistics about the dataset."""
    print(f"Total completion samples: {len(completion_samples)}")
    print(f"Total next word samples: {len(next_word_samples)}")

    # Analyze completion samples
    completion_context_lengths = [len(context.split()) for context, _, _ in completion_samples]
    partial_word_lengths = [len(partial) for _, partial, _ in completion_samples]
    full_word_lengths = [len(full) for _, _, full in completion_samples]

    # Analyze next word samples
    next_word_context_lengths = [len(context.split()) for context, _ in next_word_samples]
    next_word_lengths = [len(word) for _, word in next_word_samples]

    print("\nCompletion samples statistics:")
    print(f"  Average context length: {sum(completion_context_lengths) / len(completion_context_lengths):.2f} words")
    print(f"  Average partial word length: {sum(partial_word_lengths) / len(partial_word_lengths):.2f} chars")
    print(f"  Average full word length: {sum(full_word_lengths) / len(full_word_lengths):.2f} chars")

    print("\nNext word samples statistics:")
    print(f"  Average context length: {sum(next_word_context_lengths) / len(next_word_context_lengths):.2f} words")
    print(f"  Average next word length: {sum(next_word_lengths) / len(next_word_lengths):.2f} chars")


# ===============================
# INFERENCE FUNCTIONS
# ===============================

def load_ngram_model(model_path):
    """Load n-gram model from a file."""
    import pickle
    from collections import Counter, defaultdict

    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)

    # Convert regular dicts back to defaultdicts for convenient access
    unigrams = model_data['unigrams']

    bigrams = defaultdict(Counter)
    for k, v in model_data['bigrams'].items():
        bigrams[k] = Counter(v)

    trigrams = defaultdict(lambda: defaultdict(Counter))
    for k1, v1 in model_data['trigrams'].items():
        for k2, v2 in v1.items():
            trigrams[k1][k2] = Counter(v2)

    word_prefixes = defaultdict(Counter)
    for k, v in model_data['word_prefixes'].items():
        word_prefixes[k] = Counter(v)

    return unigrams, bigrams, trigrams, word_prefixes


def predict_next_word(context, unigrams, bigrams, trigrams, top_n=5):
    """
    Predict the next word given a context using n-gram model.

    Args:
        context: String of context words
        unigrams, bigrams, trigrams: N-gram models
        top_n: Number of top predictions to return

    Returns:
        List of (word, probability) tuples
    """
    # Clean and tokenize context
    context = clean_text(context.lower())
    words = nltk.word_tokenize(context)

    # No context, return most frequent unigrams
    if not words:
        total = sum(unigrams.values())
        return [(word, count / total) for word, count in unigrams.most_common(top_n)]

    # Single word context, use bigrams
    if len(words) == 1:
        last_word = words[0]
        if last_word in bigrams:
            total = sum(bigrams[last_word].values())
            if total > 0:
                return [(word, count / total) for word, count in bigrams[last_word].most_common(top_n)]

        # Back off to unigrams
        total = sum(unigrams.values())
        return [(word, count / total) for word, count in unigrams.most_common(top_n)]

    # Multiple word context, try trigrams
    last_word, second_last_word = words[-1], words[-2]

    if second_last_word in trigrams and last_word in trigrams[second_last_word]:
        total = sum(trigrams[second_last_word][last_word].values())
        if total > 0:
            return [(word, count / total) for word, count in trigrams[second_last_word][last_word].most_common(top_n)]

    # Back off to bigrams
    if last_word in bigrams:
        total = sum(bigrams[last_word].values())
        if total > 0:
            return [(word, count / total) for word, count in bigrams[last_word].most_common(top_n)]

    # Back off to unigrams
    total = sum(unigrams.values())
    return [(word, count / total) for word, count in unigrams.most_common(top_n)]


def complete_word(partial_word, word_prefixes, top_n=5):
    """
    Complete a partial word based on the word_prefixes model.

    Args:
        partial_word: String of the partial word
        word_prefixes: Dictionary mapping prefixes to possible completions
        top_n: Number of top completions to return

    Returns:
        List of (completion, probability) tuples
    """
    partial_word = partial_word.lower()

    if partial_word in word_prefixes:
        completions = word_prefixes[partial_word]
        total = sum(completions.values())
        if total > 0:
            return [(word, count / total) for word, count in completions.most_common(top_n)]

    # If no completions found, return empty list
    return []


def predict_with_context_and_partial(context, partial_word, unigrams, bigrams, trigrams, word_prefixes, top_n=5):
    """
    Combined prediction using both context and partial word.

    Args:
        context: String of context words
        partial_word: String of the partial word
        unigrams, bigrams, trigrams, word_prefixes: N-gram models
        top_n: Number of top predictions to return

    Returns:
        List of (completion, probability) tuples
    """
    # Get word completions based on prefix
    completions = complete_word(partial_word, word_prefixes, top_n=top_n * 2)
    if not completions:
        return []

    # If there's no context, return completions directly
    if not context.strip():
        return completions[:top_n]

    # Get next word predictions based on context
    context_predictions = predict_next_word(context, unigrams, bigrams, trigrams, top_n=top_n * 3)
    if not context_predictions:
        return completions[:top_n]

    # Create a dictionary of words predicted by context with their probabilities
    context_probs = {word: prob for word, prob in context_predictions}

    # Combine predictions by multiplying probabilities from both models
    # Only consider words that appear in completions
    combined_predictions = []
    for word, comp_prob in completions:
        if word in context_probs:
            # Combine probabilities - giving more weight to the completion probability
            combined_prob = comp_prob * 0.7 + context_probs[word] * 0.3
            combined_predictions.append((word, combined_prob))
        else:
            # If not in context predictions, reduce the probability slightly
            combined_predictions.append((word, comp_prob * 0.7))

    # Sort by probability and return top_n
    return sorted(combined_predictions, key=lambda x: x[1], reverse=True)[:top_n]


def interactive_prediction(model_path=None, unigrams=None, bigrams=None, trigrams=None, word_prefixes=None):
    """
    Interactive console for testing the prediction model.
    Either provide the model_path or all four model components.
    """
    import os

    # Load model if path is provided
    if model_path and os.path.exists(model_path):
        print(f"Loading model from {model_path}...")
        unigrams, bigrams, trigrams, word_prefixes = load_ngram_model(model_path)
    elif not all([unigrams, bigrams, trigrams, word_prefixes]):
        print("Error: Either provide model_path or all four model components.")
        return

    print("\n=== Interactive Word Prediction ===")
    print("Enter a context followed by a partial word (optional)")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("\nEnter context [partial_word]: ")
        if user_input.lower() == 'exit':
            break

        if '[' in user_input and ']' in user_input:
            # Split context and partial word
            parts = user_input.split('[')
            context = parts[0].strip()
            partial_word = parts[1].split(']')[0].strip()

            print(f"\nContext: '{context}'")
            print(f"Partial word: '{partial_word}'")

            # Combined prediction
            predictions = predict_with_context_and_partial(
                context, partial_word, unigrams, bigrams, trigrams, word_prefixes
            )

            print("\nPredictions (combined):")
            for i, (word, prob) in enumerate(predictions):
                print(f"{i + 1}. {word} ({prob:.4f})")

            # Word completion only
            completions = complete_word(partial_word, word_prefixes)
            print("\nCompletions (based only on partial word):")
            for i, (word, prob) in enumerate(completions[:5]):
                print(f"{i + 1}. {word} ({prob:.4f})")

        else:
            # Next word prediction only
            context = user_input.strip()
            print(f"\nContext: '{context}'")

            predictions = predict_next_word(context, unigrams, bigrams, trigrams)
            print("\nNext word predictions:")
            for i, (word, prob) in enumerate(predictions):
                print(f"{i + 1}. {word} ({prob:.4f})")


# Example usage:
if __name__ == "__main__":
    # This would typically be loaded from files
    sample_paragraphs = [
        "Today I went to the park. The weather was beautiful and sunny. I saw many people walking their dogs and enjoying the sunshine.",
        "I enjoy writing in my diary every day. It helps me reflect on my thoughts and experiences. Writing has become an important habit for me.",
        "The changing fortunes of time have taught me patience and resilience. Every challenge brings an opportunity to learn and grow stronger.",
        "Tomorrow I plan to visit my friend. We will go to the cinema and watch the new movie everyone is talking about. I'm looking forward to it."
    ]

    # Prepare dataset
    completion_samples, next_word_samples = prepare_diary_dataset(sample_paragraphs)

    # Analyze dataset
    analyze_dataset(completion_samples, next_word_samples)

    # Create train/val splits
    train_completion, val_completion, train_next_word, val_next_word = create_transformer_datasets(
        completion_samples, next_word_samples
    )

    # Create n-gram dataset
    unigrams, bigrams, trigrams, word_prefixes = create_ngram_dataset(sample_paragraphs)

    # Save datasets
    save_datasets(train_completion, val_completion, train_next_word, val_next_word, "word_prediction_data")

    # Save n-gram model
    save_ngram_model(unigrams, bigrams, trigrams, word_prefixes, "ngram_model.pkl")

    print("\nDataset preparation complete!")

    # Test the model with the interactive prediction tool
    print("\nStarting interactive prediction with the trained model...\n")
    interactive_prediction(unigrams=unigrams, bigrams=bigrams, trigrams=trigrams, word_prefixes=word_prefixes)

    # Alternatively, load from file and test:
    # interactive_prediction(model_path="ngram_model.pkl")