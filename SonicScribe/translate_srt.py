import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import argparse
from rich.progress import Progress, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich.console import Console
from SonicScribe.utils.language_detector import detect_language
from SonicScribe.utils.file_manager import save_transcript, save_srt_from_segments

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_args():
    parser = argparse.ArgumentParser(description="🌐 SRT Translator - Convert subtitles to English")
    parser.add_argument("--input", required=True, help="Path to input SRT file")
    parser.add_argument("--output", help="Path to output SRT file (default: input_english.srt)")
    parser.add_argument("--model", default="gpt-4o-mini", help="GPT model to use for translation")
    parser.add_argument("--bilingual", action="store_true", help="Create bilingual SRT with original and translated text")
    parser.add_argument("--language", default=None, help="Language of the input subtitles (e.g., 'en', 'fr', 'es'). If not specified, it will be auto-detected.")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Set output path if not specified
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_english{ext}"
    
    # Create console for rich output
    console = Console()
    console.print(f"[bold blue]🌐 SRT Translator[/bold blue]")
    console.print(f"📂 Input: [cyan]{args.input}[/cyan]")
    console.print(f"💾 Output: [cyan]{args.output}[/cyan]")
    console.print(f"🤖 Model: [cyan]{args.model}[/cyan]")
    console.print(f"🔤 Bilingual: [cyan]{'Yes' if args.bilingual else 'No'}[/cyan]")
    
    # Check if input file exists
    if not os.path.exists(args.input):
        console.print(f"[bold red]❌ Input file not found: {args.input}[/bold red]")
        return 1
        
    # Read the SRT content
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        console.print(f"[bold red]❌ Error reading SRT file: {e}[/bold red]")
        return 1

    # Split into subtitle blocks (each entry in the SRT file)
    subtitle_blocks = re.split(r'\n\s*\n', content)
    total_blocks = len(subtitle_blocks)
    
    console.print(f"Found [bold cyan]{total_blocks}[/bold cyan] subtitle blocks")
    
    # Detect language if not specified
    detected_language = args.language
    if not detected_language:
        console.print("[bold yellow]🌐 Detecting language of the subtitles...[/bold yellow]")
        all_text = " ".join([block.split("\n", 2)[-1] for block in subtitle_blocks if block.strip()])
        detected_language = detect_language(all_text)
        console.print(f"[bold green]🌐 Detected language: {detected_language}[/bold green]")
    
    # Process each block with progress indicator
    translated_blocks = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Translating subtitles...", total=total_blocks)
        
        for i, block in enumerate(subtitle_blocks):
            if not block.strip():
                translated_blocks.append(block)
                progress.update(task, advance=1)
                continue
            
            # Split the block into lines
            lines = block.strip().split('\n')
            
            # Need at least 3 lines for a proper subtitle block (number, timestamp, text)
            if len(lines) < 3:
                translated_blocks.append(block)
                progress.update(task, advance=1)
                continue
            
            # Extract parts
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            
            # Skip empty text or caption info like "Subtitles by..."
            if not text.strip() or "SDI Media" in text:
                translated_blocks.append(block)
                progress.update(task, advance=1)
                continue
            
            # Translate the text
            try:
                response = client.chat.completions.create(
                    model=args.model,
                    messages=[
                        {"role": "system", "content": f"You are a translation assistant. Translate {detected_language} to English."},
                        {"role": "user", "content": f"Translate this text to English: {text}"}
                    ]
                )
                
                translated_text = response.choices[0].message.content.strip()
                
                # Rebuild the subtitle block with translated text
                if args.bilingual:
                    translated_block = f"{index}\n{timestamp}\n{text}\n{translated_text}"
                else:
                    translated_block = f"{index}\n{timestamp}\n{translated_text}"
                
                translated_blocks.append(translated_block)
                
            except Exception as e:
                console.print(f"[bold yellow]⚠️ Error translating block {i+1}: {e}[/bold yellow]")
                translated_blocks.append(block)  # Keep original if translation fails
                
            progress.update(task, advance=1)

    # Write the translated SRT
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(translated_blocks))
        console.print(f"[bold green]✅ Translation completed successfully![/bold green]")
        console.print(f"Translated SRT saved to: [cyan]{args.output}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]❌ Error saving translated SRT: {e}[/bold red]")
        return 1
        
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())