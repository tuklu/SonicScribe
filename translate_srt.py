import os
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to the original SRT file
srt_file = "output/english_subs/Bukan Kahwin Paksa S1E3.srt"
output_file = "output/english_subs/Bukan Kahwin Paksa S1E3_english.srt"

# Read the SRT content
with open(srt_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Split into subtitle blocks (each entry in the SRT file)
subtitle_blocks = re.split(r'\n\s*\n', content)

# Process each block
translated_blocks = []
total_blocks = len(subtitle_blocks)

print(f"Total blocks to translate: {total_blocks}")

for i, block in enumerate(subtitle_blocks):
    if not block.strip():
        continue
    
    # Split the block into lines
    lines = block.strip().split('\n')
    
    # Need at least 3 lines for a proper subtitle block (number, timestamp, text)
    if len(lines) < 3:
        translated_blocks.append(block)  # Keep as is if not a proper block
        continue
    
    # Extract parts
    index = lines[0]
    timestamp = lines[1]
    text = '\n'.join(lines[2:])
    
    # Skip empty text or caption info
    if "SDI Media" in text or not text.strip():
        translated_blocks.append(block)
        print(f"Block {i+1}/{total_blocks}: Skipped (caption info)")
        continue
    
    # Translate the text
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a translation assistant. Translate the following Malay text to English."},
                {"role": "user", "content": f"Translate this text to English: {text}"}
            ]
        )
        
        translated_text = response.choices[0].message.content.strip()
        
        # Rebuild the subtitle block with translated text
        translated_block = f"{index}\n{timestamp}\n{translated_text}"
        translated_blocks.append(translated_block)
        
        print(f"Block {i+1}/{total_blocks}: Translated")
    
    except Exception as e:
        print(f"Error translating block {i+1}: {e}")
        # Keep original if translation fails
        translated_blocks.append(block)

# Write the translated SRT
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(translated_blocks))

print(f"\nTranslation completed successfully!")
print(f"Translated SRT saved to: {output_file}")