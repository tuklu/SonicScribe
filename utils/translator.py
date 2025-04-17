from openai import OpenAI
import os
import re
from dotenv import load_dotenv
import time
import logging
import math
from typing import List, Dict, Any

logger = logging.getLogger("SonicScribe")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def translate_segments_to_english(segments: List[Dict[str, Any]], batch_size=10, model="gpt-4o-mini", source_language="unknown") -> List[Dict[str, Any]]:
    # Translate segments to English in batches, preserving the original text.
    if not segments:
        logger.warning("No segments to translate")
        return []
    
    # Check API key
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return segments
        
    logger.info(f"Starting translation of {len(segments)} segments in {math.ceil(len(segments)/batch_size)} batches")
    logger.info(f"Source language: {source_language}")
    
    translated_segments = []
    
    # Process in batches
    for batch_idx in range(0, len(segments), batch_size):
        end_idx = min(batch_idx + batch_size, len(segments))
        current_batch = segments[batch_idx:end_idx]
        
        logger.info(f"Translating batch {batch_idx//batch_size + 1}/{math.ceil(len(segments)/batch_size)} ({len(current_batch)} segments)...")
        
        # Prepare batch request with simpler format
        messages = [
            {"role": "system", "content": f"You are a translation assistant. Translate {source_language} to English accurately."},
            {"role": "user", "content": "Translate each of these numbered segments to English. Return ONLY the translations, one per line, preserving the numbering:"}
        ]
        
        # Add each segment as a numbered item
        for i, segment in enumerate(current_batch):
            messages[1]["content"] += f"\n{i+1}. {segment['text']}"
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            
            # Parse the response - should be one translation per line
            translated_text = response.choices[0].message.content.strip()
            translated_lines = translated_text.split('\n')
            
            # Match translations with original segments
            for i, segment in enumerate(current_batch):
                # Try to find a matching numbered line
                matching_line = None
                for line in translated_lines:
                    # Look for lines with the format "1. Translated text" or just numbered lines
                    match = re.match(rf'^{i+1}\.\s*(.*)', line.strip())
                    if match:
                        matching_line = match.group(1)
                        break
                
                if matching_line:
                    # Create a new segment with both original and translated text
                    translated_segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": matching_line,
                        "original_text": segment["text"]
                    })
                else:
                    # If no match found, keep original
                    translated_segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"],
                        "original_text": segment["text"]
                    })
            
            # Small delay to prevent rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Translation error in batch {batch_idx//batch_size + 1}: {e}")
            # Add original segments if there's an error
            for segment in current_batch:
                translated_segments.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"],
                    "original_text": segment["text"]
                })
            time.sleep(2)  # Longer delay after an error
    
    logger.info(f"Translation completed: {len(translated_segments)} segments processed")
    return translated_segments