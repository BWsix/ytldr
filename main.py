#!/usr/bin/env python3
"""
YouTube Video Summarizer

A tool to download YouTube videos, transcribe them with Whisper,
and generate summaries using Ollama.
"""

import argparse
import os
import sys
from pathlib import Path

from ytldr.downloader import download_video, get_metadata
from ytldr.transcriber import transcribe_audio
from ytldr.summarizer import summarize_video
from ytldr.utils import generate_markdown, save_markdown, sanitize_title_for_directory


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube video, transcribe with Whisper, and summarize with Ollama"
    )
    parser.add_argument(
        "url",
        help="YouTube video URL"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for all video summaries (default: ./output)"
    )
    parser.add_argument(
        "--working-dir",
        help="Working directory for current video (default: video title from yt-dlp)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="summary.md",
        help="Output markdown file (default: summary.md)"
    )
    parser.add_argument(
        "--model",
        default="gemma3:12b",
        help="Ollama model to use for summarization (default: gemma3:12b)"
    )
    parser.add_argument(
        "--no-keep-temp",
        action="store_true",
        help="Remove working directory files after processing (default: keep files)"
    )
    
    args = parser.parse_args()
    
    # Validate URL (only if not help and URL is provided)
    if hasattr(args, 'url') and args.url and ("youtube.com" not in args.url and "youtu.be" not in args.url):
        print("Error: Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        print(f"Processing: {args.url}")
        print(f"Output directory: {output_dir}")
        print(f"Output file: {args.output}")
        print(f"Model: {args.model}")
        print("-" * 50)
        
        # Step 1: Get video metadata and create working directory
        print("Step 1: Getting video metadata...")
        metadata = get_metadata(args.url)
        print(f"✓ Metadata: {metadata}")
        
        # Create working directory for this video
        if args.working_dir:
            working_dir_name = args.working_dir
        else:
            # Sanitize video title for use as directory name
            working_dir_name = sanitize_title_for_directory(metadata['title'])
        
        working_dir = output_dir / working_dir_name
        working_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Working directory: {working_dir}")
        
        # Step 2: Download video and extract metadata
        print("Step 2: Downloading video...")
        metadata = download_video(args.url, str(working_dir))
        print(f"✓ Downloaded: {metadata['title']}")
        print(f"✓ Duration: {metadata['duration']} seconds")
        print(f"✓ Chapters found: {len(metadata.get('chapters', []))}")
        
        # Step 3: Transcribe audio
        print("\nStep 3: Transcribing audio...")
        transcript = transcribe_audio(metadata['audio_file'], str(working_dir))
        print(f"✓ Transcribed {len(transcript['segments'])} segments")
        print(f"✓ Language: {transcript['language']}")
        
        # Step 4: Generate summary
        print("\nStep 4: Generating summary...")
        summary_data = summarize_video(transcript, metadata, args.model, str(working_dir))
        print(f"✓ Generated summary with {len(summary_data['chapters'])} chapters")
        
        # Step 5: Generate markdown
        print("\nStep 5: Generating markdown...")
        markdown = generate_markdown(summary_data)
        output_file = working_dir / args.output
        save_markdown(markdown, str(output_file))
        print(f"✓ Saved summary to: {output_file}")
        
        # Cleanup
        if args.no_keep_temp:
            print("\nCleaning up temporary files...")
            for file in working_dir.glob("*"):
                if file.is_file():
                    file.unlink()
            working_dir.rmdir()
            print("✓ Cleaned up")
        
        print("\n🎉 Summary complete!")
        print(f"📄 View your summary: {output_file}")
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 