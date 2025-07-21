# ytldr - YouTube Video Summarizer

A powerful tool to download YouTube videos, transcribe them with Whisper, and generate comprehensive summaries using Ollama.

## Features

- **Video Download**: Downloads YouTube videos as high-quality audio using yt-dlp
- **Speech Transcription**: Converts audio to text with timestamps using OpenAI Whisper
- **AI Summarization**: Generates detailed summaries using Ollama (supports multiple models)
- **Chapter Support**: Automatically detects and summarizes video chapters
- **Timestamp Links**: Creates clickable YouTube timestamp links in summaries
- **Multi-language**: Supports transcription and summarization in multiple languages
- **Markdown Output**: Generates well-formatted markdown summaries

## Prerequisites

### Required Software

1. **Python 3.9**
2. **FFmpeg** - For audio processing
3. **Ollama** - For AI summarization

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg website](https://ffmpeg.org/download.html)

### Install Ollama

Follow the [Ollama installation guide](https://ollama.ai/download) for your platform.

After installation, pull a model:
```bash
ollama pull gemma3:12b
```

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ytldr
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
python main.py --help
```

## Usage

### Basic Usage

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Advanced Usage

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" \
    --output-dir ./summaries \
    --model llama3.1:8b \
    --output detailed_summary.md \
    --no-keep-temp
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | YouTube video URL | Required |
| `--output-dir` | Output directory for summaries | `./output` |
| `--working-dir` | Custom working directory name | Video title |
| `--output` | Output markdown filename | `summary.md` |
| `--model` | Ollama model for summarization | `gemma3:12b` |
| `--no-keep-temp` | Remove temporary files after processing | Keep files |

## How It Works

1. **Metadata Extraction**: Gets video info, title, duration, and chapters
2. **Audio Download**: Downloads video as MP3 audio using yt-dlp
3. **Transcription**: Converts audio to text with timestamps using Whisper
4. **Summarization**: Generates summaries using Ollama with chapter support
5. **Markdown Generation**: Creates formatted markdown with timestamp links

## Output Structure

```
output/
├── Video_Title/
│   ├── audio.mp3              # Downloaded audio file
│   ├── transcript.json        # Full transcript with timestamps
│   ├── transcript.txt         # Plain text transcript
│   ├── video_metadata.json    # Video metadata and chapters
│   ├── summary.md            # Generated summary
│   ├── summary_data.json     # Raw summary data
│   └── chapter_*.json        # Individual chapter summaries
```

## Example Output

```markdown
# Brian Kernighan: UNIX, C, AWK, AMPL, and Go Programming | Lex Fridman Podcast #109

**Duration:** 1:43:09 | **Language:** English | **Chapters:** 19

## Table of Contents

- [Video Information](#video-information)
- [Summary](#summary)
- [Chapter Summaries](#chapter-summaries)
  - [1. 0:00 - 4:24 Introduction](#1-000-424-introduction)
  - [2. 4:24 - 22:09 UNIX early days](#2-424-2209-unix-early-days)
  - ...

## Video Information

**Channel:** Lex Fridman
**Original URL:** [https://www.youtube.com/watch?v=O9upVbGSBFo](https://www.youtube.com/watch?v=O9upVbGSBFo)

## Summary

This comprehensive video covers multiple topics with detailed explanations and practical examples.

## Chapter Summaries

### 1. [0:00 - 4:24] Introduction

This introductory segment of the podcast establishes the guest and provides a detailed overview of the show's sponsors [0:00]. The conversation will feature Brian Kernighan, a highly influential figure in computer science, renowned for his work alongside Ken Thompson and Dennis Ritchie during the early days of Unix. Kernighan's contributions extend far beyond Unix, including co-authoring "The C Programming Language" with Ritchie – a seminal text in the field [0:10]. He's also authored numerous other books on programming and related topics, showcasing his breadth of knowledge and experience. Notably, he co-created AUK, a text processing language utilized by Linux developers, and Ample, an algebraic modeling language that the host personally appreciates for its optimization capabilities [0:37]. Despite his extensive achievements, Kernighan is described as remarkably humble and kind.

**Important Moments:**
- **[0:10](https://www.youtube.com/watch?v=O9upVbGSBFo&t=10s)** - Introduction to Brian Kernighan's contributions
- **[0:37](https://www.youtube.com/watch?v=O9upVbGSBFo&t=37s)** - Discussion of AWK and AMPL languages

### 2. [4:24 - 22:09] UNIX early days

The discussion delves into the early days of Unix, exploring its origins and the collaborative environment that fostered its development. The speaker recounts the unique circumstances at Bell Labs during the late 1960s and early 1970s, where a small group of researchers had unprecedented freedom to explore and create [4:30]. This environment allowed for the development of Unix, which was initially created as a personal computing environment for Ken Thompson [4:45]. The speaker emphasizes the collaborative nature of the project, where ideas were freely shared and improved upon by the entire team [5:15].

**Important Moments:**
- **[4:30](https://www.youtube.com/watch?v=O9upVbGSBFo&t=270s)** - Bell Labs research environment
- **[4:45](https://www.youtube.com/watch?v=O9upVbGSBFo&t=285s)** - Unix as personal computing environment
- **[5:15](https://www.youtube.com/watch?v=O9upVbGSBFo&t=315s)** - Collaborative development process

...
```

## Examples

The `examples/` folder contains sample outputs from real YouTube videos to demonstrate the tool's capabilities:

```
examples/
└── Brian_Kernighan_UNIX_C_AWK_AMPL_and_Go_Programming_Lex_Fridman_Podcast_109/
    ├── audio.mp3              # Downloaded audio file
    ├── transcript.json        # Full transcript with timestamps
    ├── transcript.txt         # Plain text transcript
    ├── video_metadata.json    # Video metadata and chapters
    ├── summary.md            # Generated summary
    ├── summary_data.json     # Raw summary data
    └── chapter_*.json        # Individual chapter summaries
```

This example shows a complete processing of a 2+ hour podcast episode with 19 chapters, demonstrating the tool's ability to handle long-form content with detailed chapter breakdowns.

## Supported Models

Any Ollama model can be used. Popular options:

- `gemma3:12b` - Good balance of speed and quality (default)
- `llama3.1:8b` - Fast and efficient
- `llama3.1:70b` - Highest quality (requires more RAM)
- `mistral:7b` - Good multilingual support

## Troubleshooting

### Common Issues

1. **"Failed to call Ollama"**
   - Ensure Ollama is running: `ollama serve`
   - Check if model is installed: `ollama list`

2. **"FFmpeg not found"**
   - Install FFmpeg following the prerequisites section

3. **"CUDA out of memory"**
   - Use a smaller model: `--model llama3.1:8b`
   - Close other GPU applications

4. **"Invalid YouTube URL"**
   - Ensure URL is from youtube.com or youtu.be
   - Check if video is available in your region

### Performance Tips

- Use smaller models for faster processing
- Enable `--no-keep-temp` to save disk space
- Process videos in batches for efficiency

## Development

### Running Tests

```bash
pip install -r requirements-dev.txt
python run_tests.py
```

### Project Structure

```
ytldr/
├── main.py              # CLI entry point
├── ytldr/
│   ├── downloader.py    # Video download and metadata
│   ├── transcriber.py   # Speech-to-text conversion
│   ├── summarizer.py    # AI summarization
│   └── utils.py         # Utilities and markdown generation
├── tests/               # Test suite
├── examples/            # Sample outputs and demonstrations
└── output/              # Generated summaries (created by tool)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech transcription
- [Ollama](https://ollama.ai/) - Local AI models
