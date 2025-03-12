import random
import re

def create_better_samples(text, window_size=10, step_size=4):
    words = re.findall(r"\b\w+\b|[^\w\s]", text)  # Tokenize properly
    samples = []

    for i in range(0, len(words) - 1, step_size):
        input_text = " ".join(words[max(0, i - window_size):i + 1])
        target_text = words[i + 1]

        # If target is punctuation, try the next actual word
        while target_text in {",", ".", "?", "!", ";", ":"} and (i + 2) < len(words):
            i += 1
            target_text = words[i + 1]

        # Skip bad samples (e.g., input is just punctuation)
        if re.fullmatch(r"[^\w]+", input_text.strip()):
            continue

        samples.append((input_text, target_text))

    return samples


def create_mixed_samples(text, window_size=10, step_size=4, trunc_prob=0.3):
    words = re.findall(r"\b\w+\b|[^\w\s]", text)  # Tokenize words + punctuation
    samples = []

    for i in range(1, len(words)):
        input_text = " ".join(words[max(0, i - window_size):i])
        target_text = words[i]

        # Add normal next-word prediction case
        samples.append((input_text, target_text))

        # Randomly add a truncated word sample (for mid-word prediction)
        if random.random() < trunc_prob and len(target_text) > 2:
            truncated_input = input_text + " " + target_text[:random.randint(1, len(target_text) - 1)]
            samples.append((truncated_input, target_text))

    return samples

# Example paragraph
paragraph = "Today was a beautiful day. The sun was shining, and the birds were singing. I went for a walk in the park."

# Extract training pairs
dataset = create_mixed_samples(paragraph, window_size=10, step_size=5)

# Print some examples
for inp, out in dataset[:15]:
    print(f"Input: {inp}  --> Target: {out}")
