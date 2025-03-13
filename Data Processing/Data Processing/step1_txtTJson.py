import json
import re
import os

# Create Data directory if it doesn't exist
os.makedirs('Data', exist_ok=True)

# Read the input file
with open('Data/cleaned_diary.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Remove code blocks and any markdown formatting
text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

# Split the text by empty lines first - each paragraph block is a potential entry
paragraphs = re.split(r'\n\s*\n', text)
processed_sentences = []

for paragraph in paragraphs:
    paragraph = paragraph.strip()
    if not paragraph:  # Skip if the paragraph is empty after stripping
        continue

    # Process the paragraph to find sentence breaks at dots
    buffer = ""
    current_position = 0

    while current_position < len(paragraph):
        char = paragraph[current_position]
        buffer += char

        # Check if we have a standalone period at the end of a sentence
        is_final_dot = (
                char == '.' and
                (current_position == len(paragraph) - 1 or paragraph[
                    current_position + 1] != '.') and  # not followed by another dot
                (current_position == 0 or paragraph[current_position - 1] != '.') and  # not preceded by another dot
                len(buffer.strip()) >= 30  # buffer is long enough
        )

        if is_final_dot:
            # Process this sentence
            sentence = buffer.lower().strip()
            sentence = re.sub(r'[^\w\s.,;:!?"-]', '', sentence)  # Keep quotes for context
            sentence = re.sub(r'\s+', ' ', sentence).strip()  # Clean whitespace
            sentence = re.sub(r'-{2,}', '', sentence)  # Remove any remaining consecutive dashes

            if sentence:
                processed_sentences.append(sentence)

            buffer = ""  # Reset buffer

        current_position += 1

    # If there's remaining text that didn't end with a qualifying period,
    # or wasn't long enough, add it as its own entry
    if buffer.strip():
        sentence = buffer.lower().strip()
        sentence = re.sub(r'[^\w\s.,;:!?"-]', '', sentence)  # Keep quotes for context
        sentence = re.sub(r'\s+', ' ', sentence).strip()  # Clean whitespace
        sentence = re.sub(r'\s*-{2,}\s*', '', sentence)

        if sentence:
            processed_sentences.append(sentence)

# Save as JSON in the required format
with open('Data/raw_diary.json', 'w', encoding='utf-8') as outfile:
    json.dump(processed_sentences, outfile, ensure_ascii=False, indent=2)

print(f"Processed {len(processed_sentences)} sentences and saved to 'Data/raw_diary.json'")