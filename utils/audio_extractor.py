import os
from moviepy import VideoFileClip, AudioFileClip
import logging

logger = logging.getLogger("SonicScribe")

def extract_audio(input_path, output_dir="output/transcripts"):
    """Extract audio from video/audio files with proper resource management"""
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.wav")

    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Extracting audio from: {input_path}")
    clip = None
    
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        if input_path.lower().endswith((".mp4", ".mkv", ".mov", ".webm", ".avi", ".flv")):
            clip = VideoFileClip(input_path)
            if clip.audio is None:
                raise ValueError("No audio track found in video file")
            clip.audio.write_audiofile(output_path, codec="pcm_s16le", logger=None)
        elif input_path.lower().endswith((".mp3", ".aac", ".m4a", ".flac", ".ogg", ".wav")):
            clip = AudioFileClip(input_path)
            clip.write_audiofile(output_path, codec="pcm_s16le", logger=None)
        else:
            raise ValueError(f"Unsupported file format: {os.path.splitext(input_path)[1]}")
    
        logger.info(f"Audio saved to: {output_path}")
        return output_path
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        return None
    
    finally:
        # Make sure to close the clip to release resources
        if clip is not None:
            try:
                clip.close()
                logger.debug("Clip resources released")
            except Exception as e:
                logger.error(f"Error closing clip: {e}")