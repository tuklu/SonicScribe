from openai import OpenAI
import os
from dotenv import load_dotenv
import time
import logging
import math
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("SonicScribe")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _translate_batch(batch_texts, model="gpt-4o"):
    """Translate a batch of texts with retry mechanism"""
    prompt = "Translate the following segments to English. Return only the translations in the same numbered format:\n\n" + "\n\n".join(batch_texts)
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

def translate_segments_to_english(segments: List[Dict[str, Any]], batch_size=10, model="gpt-4o") -> List[Dict[str, Any]]:
    """
    Translate segments to English in batches to improve efficiency.
    """
    if not segments:
        logger.warning("No segments to translate")
        return []
        
    # Check API key
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return segments  # Return original segments if no API key
    
    translated_segments = []
    total_batches = math.ceil(len(segments) / batch_size)
    
    logger.info(f"Starting translation of {len(segments)} segments in {total_batches} batches")
    
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(segments))
        current_batch = segments[start_idx:end_idx]
        
        # Skip empty batches
        if not current_batch:
            continue
            
        # Prepare batch for translation
        batch_texts = [f"Segment {i+1}: {seg['text'].strip()}" for i, seg in enumerate(current_batch)]
        
        try:
            logger.info(f"Translating batch {batch_idx+1}/{total_batches} ({len(current_batch)} segments)...")
            
            translated_batch_text = _translate_batch(batch_texts, model)
            
            # Parse the response - expecting numbered format
            translated_lines = translated_batch_text.split("\n")
            
            # Process translated lines
            current_segment = None
            segment_text = ""
            segment_index = 0
            
            for line in translated_lines:
                line = line.strip()
                if not line:
                    # Process accumulated segment text if we have a current segment
                    if current_segment is not None and segment_text:
                        translated_segments.append({
                            "start": current_batch[current_segment]["start"],
                            "end": current_batch[current_segment]["end"],
                            "text": segment_text.strip()
                        })
                        segment_text = ""
                    continue
                
                # Check for segment marker (e.g., "Segment 1:" or just "1:")
                import re
                segment_match = re.match(r"(?:Segment\s+)?(\d+):\s*(.*)", line)
                
                if segment_match:
                    # Save previous segment if exists
                    if current_segment is not None and segment_text:
                        translated_segments.append({
                            "start": current_batch[current_segment]["start"],
                            "end": current_batch[current_segment]["end"],
                            "text": segment_text.strip()
                        })
                    
                    # Start new segment
                    segment_num = int(segment_match.group(1)) - 1  # 0-based index
                    if 0 <= segment_num < len(current_batch):
                        current_segment = segment_num
                        segment_text = segment_match.group(2)
                    else:
                        logger.warning(f"Invalid segment number in translation: {segment_match.group(1)}")
                        current_segment = None
                        segment_text = ""
                else:
                    # Add to current segment text
                    if current_segment is not None:
                        segment_text += " " + line
            
            # Add the last segment if needed
            if current_segment is not None and segment_text:
                translated_segments.append({
                    "start": current_batch[current_segment]["start"],
                    "end": current_batch[current_segment]["end"],
                    "text": segment_text.strip()
                })
            
            # Check if we processed all segments in batch
            if len(translated_segments) < start_idx + len(current_batch):
                logger.warning(f"Translation parsing issue in batch {batch_idx+1} - some segments may be missing")
                # Add any missing segments from the original batch
                processed_indices = [seg_idx for seg_idx in range(len(current_batch)) 
                                    if start_idx + seg_idx < len(translated_segments)]
                for i in range(len(current_batch)):
                    if i not in processed_indices:
                        translated_segments.append(current_batch[i])
            
            # Adaptive delay based on batch size
            delay = min(2.0, 0.2 * len(current_batch))
            time.sleep(delay)
            
        except Exception as e:
            logger.error(f"Translation error in batch {batch_idx+1}: {e}")
            # Fall back to original segments for this batch
            translated_segments.extend(current_batch)
            # Longer delay after an error
            time.sleep(5)
    
    logger.info(f"Translation completed: {len(translated_segments)} segments processed")
    return translated_segments