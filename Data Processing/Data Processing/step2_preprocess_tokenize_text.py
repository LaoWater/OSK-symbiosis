import json
import nltk

nltk.download('punkt')  # Download the tokenizer model if not already installed


def preprocess_paragraph(paragraph):
    """Tokenize the paragraph into words and convert to lowercase."""
    tokens = nltk.word_tokenize(paragraph.lower())
    return tokens


# Load the raw diary data with UTF-8 encoding
with open(r'Data\raw_diary.json', 'r', encoding='utf-8') as f:
    raw_paragraphs = json.load(f)

# Preprocess each paragraph
preprocessed_data = [preprocess_paragraph(p) for p in raw_paragraphs]

# Save the preprocessed data with UTF-8 encoding
with open(r'Data\preprocessed_diary.json', 'w', encoding='utf-8') as f:
    json.dump(preprocessed_data, f, indent=4, ensure_ascii=False)

print("Preprocessed data saved to 'preprocessed_diary.json'")
