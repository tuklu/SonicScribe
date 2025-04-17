# 🎙️ SonicScribe

A powerful CLI tool and Python module for transcribing and translating audio/video files using OpenAI's Whisper and GPT models.

## Features

- 🎬 Extract audio from various video and audio formats
- 🔤 Transcribe audio using OpenAI's Whisper API
- 🌐 Translate transcriptions to English or other languages
- 📝 Generate transcript and subtitle files (SRT)
- 🗣️ Support for bilingual subtitles
- 📊 Smart handling of large files by automatic chunking
- ⚡ Interactive language selection with auto-detection support
- 🛠️ Modular design for use as a Python library
- 📈 Progress indicators and detailed logging

---

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/tuklu/SonicScribe.git
   cd SonicScribe/SonicScribe
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your OpenAI API key:
   ```properties
   OPENAI_API_KEY=your_api_key_here
   ```

---

## Usage

### Main Transcription and Translation

The main script provides full functionality for processing audio/video files:

```bash
python main.py --input "path/to/your/video.mp4" --translate --output-dir "output/folder"
```

#### Options

- `--input`: Path to input audio/video file (required)
- `--translate`: Enable translation to English (optional)
- `--language`: Specify the language of the input file (e.g., `en`, `fr`, `es`). If not provided, auto-detection will be used.
- `--output-dir`: Directory to save output files (default: `output/transcripts`)
- `--whisper-model`: Model to use for transcription (default: `whisper-1`)
- `--gpt-model`: Model to use for translation (default: `gpt-4o-mini`)
- `--chunk-size`: Size of chunks in MB for large files (default: 20)
- `--verbose` or `-v`: Enable verbose logging
- `--bilingual`: Create bilingual subtitles with both original and translated text

---

### Interactive Language Selection

When processing files, SonicScribe provides an interactive language selection feature:
- You can select a language from a predefined list using arrow keys.
- You can manually input a language code by typing `/`.
- If no language is selected, SonicScribe will auto-detect the language using GPT, with a warning about potential additional API costs.

---

### Standalone SRT Translation

If you already have an SRT file and just want to translate it:

```bash
python translate_srt.py --input "path/to/your/subtitles.srt" --bilingual
```

#### Options

- `--input`: Path to input SRT file (required)
- `--output`: Path to output SRT file (default: `input_english.srt`)
- `--model`: GPT model to use for translation (default: `gpt-4o-mini`)
- `--bilingual`: Create bilingual SRT with original and translated text
- `--language`: Specify the language of the input subtitles. If not provided, auto-detection will be used.

---

## Examples

### Basic Transcription

```bash
python main.py --input "lecture.mp4"
```

This will:
- Extract audio from `lecture.mp4`
- Transcribe the audio using Whisper API
- Save a transcript and SRT file to the default output directory

### Transcription with Translation

```bash
python main.py --input "foreign_movie.mp4" --translate --gpt-model "gpt-4o"
```

This will:
- Extract audio from `foreign_movie.mp4`
- Transcribe the audio using Whisper API
- Translate the transcription to English using GPT-4o
- Save all output files to the default directory

### Bilingual Subtitles

```bash
python main.py --input "interview.mp3" --translate --bilingual
```

This will:
- Extract audio from `interview.mp3`
- Transcribe the audio using Whisper API
- Translate the transcription to English
- Create a bilingual SRT file with both original and translated text

### Translating Existing Subtitles

```bash
python translate_srt.py --input "movie.srt" --bilingual --model "gpt-4o-mini"
```

This will:
- Read the existing SRT file
- Translate the subtitles to English using GPT-4o-mini
- Create a bilingual SRT with both original and translated text

---

## Output Files

SonicScribe generates several types of output files:

- `{filename}_transcribed.txt`: Plain text transcript
- `{filename}.srt`: SRT subtitle file with timestamps
- `{filename}_bilingual.srt`: Optional bilingual SRT file (when using `--bilingual`)
- `{filename}_english.srt`: Translated SRT file (when using `translate_srt.py`)

---

## Handling Large Files

SonicScribe automatically handles large audio files:

- Files smaller than 25MB are processed directly through the Whisper API.
- Larger files are split into chunks, processed separately, and then recombined.
- The `--chunk-size` parameter controls the size of these chunks (default: 20MB).

---

## Troubleshooting

### API Key Issues

If you encounter "API key not found" errors:
- Ensure your `.env` file exists in the project root directory.
- Verify that your API key is correct and active.
- Try setting the API key directly in your environment.

### File Format Problems

If SonicScribe fails to process your file:
- Verify the file exists and is not corrupted.
- Check that the format is supported (mp4, mkv, mov, mp3, wav, etc.).
- Try converting the file to a more standard format like MP4 or WAV.

### Memory Issues with Large Files

If you encounter memory errors with very large files:
- Try reducing the `--chunk-size` parameter.
- Ensure your system has sufficient free memory.
- Consider pre-splitting very large files manually.

---

## Limitations

- OpenAI API rate limits may affect processing speed.
- Transcription quality depends on audio clarity.
- Translation quality varies by language and content complexity.
- Processing very large files (multiple hours) can take significant time.

---

## Logging

SonicScribe logs all operations to the `logs` directory. If you encounter issues, check the log files for detailed information. Use the `--verbose` flag for more detailed logging.

---

## License

[Your license information here]

---

## Support

For issues, questions, or contributions, please [create an issue](https://github.com/yourusername/sonicscribe/issues) on the GitHub repository.