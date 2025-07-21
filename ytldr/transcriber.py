"""
Transcription module using OpenAI Whisper.
Handles speech-to-text conversion with timestamps.
"""

import json
import os
from typing import Dict, List
import whisper
import torch


def transcribe_audio(audio_file: str, output_dir: str) -> Dict:
    """
    Transcribe audio file using Whisper.
    
    Args:
        audio_file: Path to audio file
        output_dir: Directory to save transcript
        
    Returns:
        Dict containing transcript data
    """
    print("Loading Whisper model (turbo)...")
    model = whisper.load_model("turbo")
    
    print("Transcribing audio...")
    result = model.transcribe(audio_file, word_timestamps=True)
    
    # Process segments for better formatting
    segments = []
    for segment in result["segments"]:
        segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })
    
    transcript_data = {
        "segments": segments,
        "full_text": result["text"],
        "language": result["language"]
    }
    
    # Save transcript
    transcript_file = os.path.join(output_dir, "transcript.json")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    # Also save as plain text for easier reading
    text_file = os.path.join(output_dir, "transcript.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(transcript_data["full_text"])
    
    # Clean up model to free memory
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return transcript_data 