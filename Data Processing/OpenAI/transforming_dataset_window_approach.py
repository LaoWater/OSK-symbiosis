import re


def create_samples(text, window_size=10, step_size=4):
    words = re.findall(r"\b\w+\b|[^\w\s]", text)  # Keep words & punctuation
    samples = []

    for i in range(0, len(words) - window_size, step_size):
        input_text = " ".join(words[i:i + window_size])
        target_text = words[i + window_size] if i + window_size < len(words) else "<END>"
        samples.append((input_text, target_text))

    return samples


# Example paragraph
paragraph = "Today was a beautiful day. The sun was shining, and the birds were singing. I went for a walk in the park."

# Extract training pairs
dataset = create_samples(paragraph, window_size=10, step_size=5)

# Print some examples
for inp, out in dataset[:5]:
    print(f"Input: {inp}  --> Target: {out}")
