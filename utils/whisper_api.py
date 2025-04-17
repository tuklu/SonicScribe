import os
from openai import OpenAI
from dotenv import load_dotenv
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from pydub import AudioSegment

logger = logging.getLogger("SonicScribe")

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def transcribe_audio(audio_path, model="whisper-1"):
    # Transcribe audio with retry mechanism
    logger.info(f"Sending audio to Whisper API using model: {model}")

    # Validate input file
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return None
    
    # Check API key
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return None

    try:
        with open(audio_path, "rb") as audio_file:
            logger.info("Starting transcription request...")
            start_time = time.time()
            
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format="verbose_json"
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"Transcription completed in {elapsed_time:.2f} seconds")
            
            # Log basic stats about the response
            if hasattr(response, "segments"):
                logger.info(f"Received {len(response.segments)} segments")
            
            return response
            
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        raise

def split_audio_file(audio_path, output_dir, chunk_size_mb=20):
    # Split audio file into chunks of specified size using pydub
    import math
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Splitting audio file: {audio_path}")
    
    # Load audio file
    audio = AudioSegment.from_wav(audio_path)
    
    # Calculate duration in milliseconds
    total_duration_ms = len(audio)
    total_size = os.path.getsize(audio_path)
    
    # Calculate how many milliseconds per chunk based on file size
    ms_per_mb = total_duration_ms / (total_size / (1024 * 1024))
    ms_per_chunk = ms_per_mb * chunk_size_mb
    
    # Convert to integer
    ms_per_chunk = int(ms_per_chunk)
    
    logger.info(f"Audio duration: {total_duration_ms/1000} seconds, splitting into ~{ms_per_chunk/1000} second chunks")
    
    # Create chunks
    chunks = []
    total_chunks = math.ceil(total_duration_ms / ms_per_chunk)
    
    for i in range(total_chunks):
        start_ms = i * ms_per_chunk
        end_ms = min(start_ms + ms_per_chunk, total_duration_ms)
        
        chunk_path = os.path.join(output_dir, f"chunk_{i+1}.wav")
        chunk_audio = audio[start_ms:end_ms]
        chunk_audio.export(chunk_path, format="wav")
        
        chunks.append(chunk_path)
        logger.info(f"Created chunk {i+1}/{total_chunks}: {start_ms/1000}-{end_ms/1000} seconds")
    
    return chunks

def transcribe_large_audio(audio_path, model="whisper-1", chunk_size_mb=20):
    # Split and transcribe large audio files using Whisper API
    logger.info(f"Audio file may be too large, splitting into chunks")
    
    # Create a directory for chunks
    chunk_dir = os.path.join(os.path.dirname(audio_path), "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    
    # Split audio into chunks
    chunks = split_audio_file(audio_path, chunk_dir, chunk_size_mb)
    logger.info(f"Split audio into {len(chunks)} chunks")
    
    # Process each chunk
    all_segments = []
    total_duration = 0
    
    for i, chunk_path in enumerate(chunks):
        logger.info(f"Transcribing chunk {i+1}/{len(chunks)}")
        
        try:
            chunk_response = transcribe_audio(chunk_path, model)
            
            if hasattr(chunk_response, "segments") and chunk_response.segments:
                # Convert TranscriptionSegment objects to dictionaries and adjust timestamps
                for segment in chunk_response.segments:
                    all_segments.append({
                        "start": segment.start + total_duration,
                        "end": segment.end + total_duration,
                        "text": segment.text
                    })
                
                # Get chunk duration for the next offset
                chunk_audio = AudioSegment.from_wav(chunk_path)
                total_duration += len(chunk_audio) / 1000.0  # Convert from ms to seconds
            else:
                logger.warning(f"No segments found in chunk {i+1}")
        except Exception as e:
            logger.error(f"Error transcribing chunk {i+1}: {e}")
    
    # Clean up chunks
    for chunk_path in chunks:
        try:
            os.remove(chunk_path)
        except:
            pass
    
    try:
        os.rmdir(chunk_dir)
    except:
        pass
    
    # Return combined results
    if all_segments:
        return {
            "text": " ".join([s["text"] for s in all_segments]),
            "segments": all_segments
        }
    else:
        return None