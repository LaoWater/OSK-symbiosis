import json

# Load the preprocessed diary data with UTF-8 encoding
with open(r'Data\preprocessed_diary.json', 'r', encoding='utf-8') as f:
    preprocessed_data = json.load(f)

# Extract all words from the preprocessed data
all_words = [word for paragraph in preprocessed_data for word in paragraph]

# Get unique words and sort them
vocabulary = sorted(set(all_words))

# Save the vocabulary to a new JSON file with UTF-8 encoding
with open(r'Data\vocabulary.json', 'w', encoding='utf-8') as f:
    json.dump(vocabulary, f, indent=4, ensure_ascii=False)

print("Vocabulary saved to 'vocabulary.json'")
