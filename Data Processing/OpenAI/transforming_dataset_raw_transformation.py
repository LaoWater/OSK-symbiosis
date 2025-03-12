import re
from itertools import islice


def split_text_into_sequences(text, max_length=10):
    words = re.findall(r"\b\w+\b|[^\w\s]", text)  # Keeps punctuation as separate tokens
    sequences = []

    for i in range(1, len(words)):
        input_text = " ".join(words[max(0, i - max_length):i])
        target_text = words[i]

        # Check if the last character is a partial word (incomplete typing)
        if not words[i].isalpha() and i + 1 < len(words):
            target_text = words[i + 1]  # Predict next full word instead

        sequences.append((input_text, target_text))

    return sequences


# Example paragraph
paragraph = "Today was a beautiful day. The sun was shining, and the birds were singing. I went for a walk in the park."

# Convert into input-output pairs
dataset = split_text_into_sequences(paragraph)

# Print some examples
for inp, out in islice(dataset, 10):
    print(f"Input: {inp}  --> Target: {out}")
