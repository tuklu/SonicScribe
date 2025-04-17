import argparse
import sys
import logging
import time
import os
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

from utils.audio_extractor import extract_audio
from utils.whisper_api import transcribe_audio, transcribe_large_audio
from utils.file_manager import save_transcript, save_srt_from_segments
from utils.translator import translate_segments_to_english
from utils.logger import setup_logger
from utils.language_detector import detect_language  # Add a new utility for language detection

def parse_args():
    """Parse command line arguments with expanded options"""
    parser = argparse.ArgumentParser(description="🎙️ SonicScribe - Transcribe & Translate using Whisper API")
    parser.add_argument("--input", required=True, help="Path to input audio/video file")
    parser.add_argument("--translate", action="store_true", help="Translate subtitles to English using GPT")
    parser.add_argument("--language", default=None, help="Language of the input file (e.g., 'en', 'fr', 'es'). If not specified, it will be auto-detected.")
    parser.add_argument("--output-dir", default="output/transcripts", help="Directory to save output files")
    parser.add_argument("--whisper-model", default="whisper-1", help="Whisper model to use for transcription")
    parser.add_argument("--gpt-model", default="gpt-4o-mini", help="GPT model to use for translation")
    parser.add_argument("--chunk-size", type=int, default=20, help="Chunk size in MB for large files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--bilingual", action="store_true", help="Create bilingual subtitles with original and translated text")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(log_level)
    
    # Rich console for pretty output
    console = Console()
    
    console.print(f"[bold blue]🎙️ SonicScribe[/bold blue]")
    console.print(f"📂 File: [cyan]{args.input}[/cyan]")
    console.print(f"🔁 Translate to English: [cyan]{'Yes' if args.translate else 'No'}[/cyan]")
    console.print(f"💾 Output directory: [cyan]{args.output_dir}[/cyan]")
    console.print(f"🤖 Whisper model: [cyan]{args.whisper_model}[/cyan]")
    
    if args.translate:
        console.print(f"🤖 Translation model: [cyan]{args.gpt_model}[/cyan]")
    
    start_time = time.time()
    
    # Extract audio with progress spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Extracting audio...", total=None)
        audio_path = extract_audio(args.input, args.output_dir)
        progress.update(task, completed=True)
    
    if not audio_path:
        console.print("[bold red]❌ Failed to extract audio. Exiting.[/bold red]")
        return 1
    
    # Transcribe audio with progress spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Transcribing audio...", total=None)
        try:
            # Check file size and use appropriate transcription method
            file_size = os.path.getsize(audio_path)
            if file_size > 25 * 1024 * 1024:  # 25 MB
                console.print(f"[yellow]⚠️ Audio file is too large for Whisper API ({file_size / (1024 * 1024):.2f} MB), splitting into chunks...[/yellow]")
                text_response = transcribe_large_audio(audio_path, args.whisper_model, args.chunk_size)
            else:
                console.print(f"[green]Audio file size: {file_size / (1024 * 1024):.2f} MB, using Whisper API directly[/green]")
                text_response = transcribe_audio(audio_path, args.whisper_model)
                
            progress.update(task, completed=True)
            
            if not text_response:
                console.print("[bold red]❌ Failed to transcribe audio. Exiting.[/bold red]")
                return 1
                
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[bold red]❌ Error during transcription: {e}[/bold red]")
            return 1
    
    # Process segments
    try:
        # Handle different response formats
        if hasattr(text_response, "segments"):
            segments = text_response.segments
        else:
            segments = text_response.get("segments", [])
            
        if not segments:
            console.print("[bold red]😔 No segments found in transcription response.[/bold red]")
            return 1
        
        # Store original segments before translation
        original_segments = []
        for seg in segments:
            if hasattr(seg, 'start') and hasattr(seg, 'end') and hasattr(seg, 'text'):
                original_segments.append({
                    "start": seg.start if hasattr(seg, 'start') else seg["start"],
                    "end": seg.end if hasattr(seg, 'end') else seg["end"],
                    "text": seg.text if hasattr(seg, 'text') else seg["text"]
                })
            else:
                original_segments.append(seg.copy() if hasattr(seg, 'copy') else dict(seg))
        
        # Detect language if not specified
        detected_language = args.language
        if not detected_language:
            console.print("[bold yellow]🌐 Detecting language of the transcription...[/bold yellow]")
            detected_language = detect_language(" ".join([s["text"] for s in original_segments]))
            console.print(f"[bold green]🌐 Detected language: {detected_language}[/bold green]")
        
        if args.translate:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}[/bold blue]"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Translating segments to English...", total=None)
                try:
                    translated_segments = translate_segments_to_english(
                        original_segments, 
                        batch_size=10, 
                        model=args.gpt_model,
                        source_language=detected_language
                    )
                    progress.update(task, completed=True)
                    
                    # Use translated segments for further processing
                    segments = translated_segments
                except Exception as e:
                    progress.update(task, completed=True)
                    console.print(f"[bold yellow]⚠️ Translation warning: {e}[/bold yellow]")
                    console.print("[bold yellow]⚠️ Continuing with original segments...[/bold yellow]")
        
        # Extract full text from segments
        full_text = " ".join([s["text"] for s in segments])
        
        console.print("\n[bold green]📄 Transcript Preview:[/bold green]\n")
        preview_text = full_text[:500] + ("..." if len(full_text) > 500 else "")
        console.print(f"[italic]{preview_text}[/italic]")
        
        # Save transcript and SRT files
        transcript_path = save_transcript(full_text, args.input, args.output_dir)
        srt_path = save_srt_from_segments(segments, args.input, args.output_dir)
        
        # Save bilingual SRT if requested and translation was done
        if args.translate and args.bilingual and "original_text" in segments[0]:
            from utils.file_manager import save_bilingual_srt
            bilingual_path = save_bilingual_srt(segments, args.input, args.output_dir)
            if bilingual_path:
                console.print(f"🌐 Bilingual SRT saved to: [cyan]{bilingual_path}[/cyan]")
        
        if transcript_path and srt_path:
            console.print("\n[bold green]✅ Processing complete![/bold green]")
            elapsed_time = time.time() - start_time
            console.print(f"⏱️ Total processing time: [cyan]{elapsed_time:.2f}[/cyan] seconds")
            console.print(f"📄 Transcript saved to: [cyan]{transcript_path}[/cyan]")
            console.print(f"🎬 SRT subtitles saved to: [cyan]{srt_path}[/cyan]")
        else:
            console.print("\n[bold yellow]⚠️ Processing completed with warnings.[/bold yellow]")
            return 1
    except Exception as e:
        console.print(f"[bold red]❌ Error processing transcription: {e}[/bold red]")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())