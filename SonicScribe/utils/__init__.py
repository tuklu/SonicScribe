"""
Utility modules for SonicScribe.

This package contains helper functions and modules for:
- Audio extraction
- Transcription using Whisper API
- Translation using GPT models
- File management for transcripts and subtitles
- Logging setup
- Language detection
"""

# Import key utilities for easier access
from .audio_extractor import extract_audio
from .whisper_api import transcribe_audio, transcribe_large_audio
from .translator import translate_segments_to_english
from .file_manager import save_transcript, save_srt_from_segments, save_bilingual_srt
from .logger import setup_logger
from .language_detector import detect_language