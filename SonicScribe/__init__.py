"""
🎙️ SonicScribe - A Python module for transcribing and translating audio/video files.

This package provides utilities for:
- Extracting audio from media files
- Transcribing audio using OpenAI's Whisper API
- Translating transcriptions to English using GPT models
- Generating transcript and subtitle files (SRT)
- Supporting bilingual subtitles

Modules:
- audio_extractor: Functions for extracting audio from video/audio files
- whisper_api: Functions for transcribing audio using Whisper API
- translator: Functions for translating text segments
- file_manager: Functions for saving transcripts and subtitles
- logger: Logger setup for detailed logging
- language_detector: Language detection using GPT

Example Usage:
    from sonicscribe.utils.audio_extractor import extract_audio
    from sonicscribe.utils.whisper_api import transcribe_audio
    from sonicscribe.utils.translator import translate_segments_to_english
"""

__version__ = "1.0.3"
__author__ = "Jisnu Kalita"
__email__ = "ssh@tuklu.dev"

# Import key utilities for easier access
from .utils.audio_extractor import extract_audio
from .utils.whisper_api import transcribe_audio, transcribe_large_audio
from .utils.translator import translate_segments_to_english
from .utils.file_manager import save_transcript, save_srt_from_segments, save_bilingual_srt
from .utils.logger import setup_logger
from .utils.language_detector import detect_language