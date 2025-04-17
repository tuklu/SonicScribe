import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("SonicScribe")

def save_transcript(text, original_file, output_dir="output/transcripts"):
    """Save transcript to file with proper error handling"""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(original_file))[0]
    output_path = os.path.join(output_dir, f"{base}_transcribed.txt")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"Transcript saved at: {output_path}")
        return output_path
    except IOError as e:
        logger.error(f"I/O error when saving transcript: {e}")
    except Exception as e:
        logger.error(f"Failed to save transcript: {e}")
    return None

def save_srt_from_segments(segments: List[Dict[str, Any]], original_file, output_dir="output/transcripts"):
    """Save SRT file from segments with improved formatting and error handling"""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(original_file))[0]
    output_path = os.path.join(output_dir, f"{base}.srt")

    def format_time(seconds):
        """Format time in SRT format (HH:MM:SS,mmm)"""
        # Ensure we're working with a float
        seconds = float(seconds)
        
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        # Ensure exactly 3 digits for milliseconds
        millis = int(round((seconds % 1) * 1000))
        
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments):
                # Check if segment has required keys
                if 'start' not in seg or 'end' not in seg or 'text' not in seg:
                    logger.warning(f"Skipping malformed segment: {seg}")
                    continue
                    
                start = format_time(seg['start'])
                end = format_time(seg['end'])
                f.write(f"{i + 1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(seg['text'].strip() + "\n\n")
        logger.info(f"Subtitles (with timestamps) saved at: {output_path}")
        return output_path
    except IOError as e:
        logger.error(f"I/O error when saving subtitles: {e}")
    except Exception as e:
        logger.error(f"Failed to save subtitles: {e}")
    return None

def save_bilingual_srt(segments, original_file, output_dir="output/transcripts"):
    """Save bilingual SRT file with both original and translated text"""
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(original_file))[0]
    output_path = os.path.join(output_dir, f"{base}_bilingual.srt")

    def format_time(seconds):
        """Format time in SRT format (HH:MM:SS,mmm)"""
        seconds = float(seconds)
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds % 1) * 1000))
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for i, seg in enumerate(segments):
                if 'start' not in seg or 'end' not in seg or 'text' not in seg:
                    logger.warning(f"Skipping malformed segment: {seg}")
                    continue
                    
                start = format_time(seg['start'])
                end = format_time(seg['end'])
                
                # Check if we have both original and translated text
                if 'original_text' in seg and seg['original_text'] != seg['text']:
                    text = f"{seg['original_text']}\n{seg['text']}"
                else:
                    text = seg['text']
                    
                f.write(f"{i + 1}\n")
                f.write(f"{start} --> {end}\n")
                f.write(text.strip() + "\n\n")
                
        logger.info(f"Bilingual subtitles saved at: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to save bilingual subtitles: {e}")
        return None