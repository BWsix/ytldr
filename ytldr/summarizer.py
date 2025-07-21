"""
Video summarization module using Ollama.
Handles generating summaries from transcripts with chapter support.
"""

import json
import os
import re
from typing import Dict, List, Optional
import requests


def call_ollama(prompt: str, model: str = "gemma3:12b", temperature: float = 0.7) -> str:
    """
    Call Ollama API to generate text.
    
    Args:
        prompt: Input prompt
        model: Ollama model name
        temperature: Sampling temperature
        
    Returns:
        Generated text response
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to call Ollama: {e}")


def extract_text_for_timerange(segments: List[Dict], start_time: float, end_time: float) -> str:
    """
    Extract text from transcript segments within a time range.
    
    Args:
        segments: List of transcript segments
        start_time: Start time in seconds
        end_time: End time in seconds
        
    Returns:
        Concatenated text for the time range
    """
    text_parts = []
    for segment in segments:
        if segment["start"] >= start_time and segment["end"] <= end_time:
            text_parts.append(segment["text"])
    return " ".join(text_parts)


def create_chapter_summary_prompt(chapter_title: str, chapter_text: str, language: str, segments: List[Dict], start_time: float, end_time: float) -> str:
    """
    Create prompt for summarizing a single chapter with embedded timestamps.
    
    Args:
        chapter_title: Title of the chapter
        chapter_text: Text content of the chapter
        language: Language code
        segments: All transcript segments
        start_time: Chapter start time
        end_time: Chapter end time
        
    Returns:
        Formatted prompt for Ollama
    """
    language_name = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese"}.get(language, "English")
    
    # Filter segments for this chapter and create timestamped context
    chapter_segments = [s for s in segments if s["start"] >= start_time and s["end"] <= end_time]
    
    # Create a simplified version with timestamps for context
    timestamped_text = ""
    for segment in chapter_segments:
        minutes = int(segment["start"] // 60)
        seconds = int(segment["start"] % 60)
        timestamp = f"[{minutes}:{seconds:02d}]"
        timestamped_text += f"{timestamp} {segment['text']}\n"
    
    return f"""You are an expert content summarizer. Summarize the following chapter from a video transcript in {language_name}.

Chapter Title: {chapter_title}

Timestamped Content:
{timestamped_text}

Instructions:
1. Write a comprehensive summary (200-400 words) that preserves important information
2. Use full sentences and detailed explanations, not bullet points
3. Maintain the educational value and key insights
4. Write in {language_name}
5. Focus on the most important concepts, examples, and explanations
6. Keep the tone informative and engaging
7. **IMPORTANT**: When mentioning key concepts, demonstrations, or important moments, include the timestamp in format [MM:SS] directly in the text where relevant
8. Only include timestamps for truly important moments (3-5 per chapter)
9. Integrate timestamps naturally into sentences, like "The speaker introduces the concept of prompt engineering [2:15] and explains..."

Summary:"""


def create_full_video_summary_prompt(video_title: str, full_text: str, language: str, segments: List[Dict], duration: float) -> str:
    """
    Create prompt for summarizing the entire video with embedded timestamps.
    
    Args:
        video_title: Title of the video
        full_text: Full transcript text
        language: Language code
        segments: All transcript segments
        duration: Video duration
        
    Returns:
        Formatted prompt for Ollama
    """
    language_name = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese"}.get(language, "English")
    
    # Create timestamped context for the full video
    timestamped_text = ""
    for segment in segments:
        minutes = int(segment["start"] // 60)
        seconds = int(segment["start"] % 60)
        timestamp = f"[{minutes}:{seconds:02d}]"
        timestamped_text += f"{timestamp} {segment['text']}\n"
    
    return f"""You are an expert content summarizer. Summarize the following video transcript in {language_name}.

Video Title: {video_title}

Timestamped Content:
{timestamped_text}

Instructions:
1. Write a comprehensive summary (500-800 words) that covers all major topics
2. Use full sentences and detailed explanations, not bullet points
3. Preserve important information, examples, and key insights
4. Write in {language_name}
5. Organize the summary logically, covering all main themes
6. Maintain the educational value and depth of the original content
7. **IMPORTANT**: When mentioning key concepts, demonstrations, or important moments, include the timestamp in format [MM:SS] directly in the text where relevant
8. Only include timestamps for truly important moments (5-8 for full video)
9. Integrate timestamps naturally into sentences, like "The speaker introduces the concept of prompt engineering [2:15] and explains..."

Summary:"""


def create_timestamps_prompt(chapter_title: str, chapter_text: str, segments: List[Dict], start_time: float, end_time: float, language: str) -> str:
    """
    Create prompt for extracting important timestamps from a chapter.
    
    Args:
        chapter_title: Title of the chapter
        chapter_text: Text content of the chapter
        segments: All transcript segments
        start_time: Chapter start time
        end_time: Chapter end time
        language: Language code
        
    Returns:
        Formatted prompt for Ollama
    """
    language_name = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", "ko": "Korean", "zh": "Chinese"}.get(language, "English")
    
    # Filter segments for this chapter
    chapter_segments = [s for s in segments if s["start"] >= start_time and s["end"] <= end_time]
    
    # Create a simplified version with timestamps for context
    timestamped_text = ""
    for segment in chapter_segments:
        minutes = int(segment["start"] // 60)
        seconds = int(segment["start"] % 60)
        timestamp = f"[{minutes}:{seconds:02d}]"
        timestamped_text += f"{timestamp} {segment['text']}\n"
    
    return f"""You are an expert at identifying important moments in video content. Extract 3-5 key timestamps from this chapter in {language_name}.

Chapter Title: {chapter_title}

Timestamped Content:
{timestamped_text}

Instructions:
1. Identify 3-5 most important moments in this chapter
2. Return ONLY the timestamps in format [MM:SS] followed by a brief description
3. Focus on key concepts, demonstrations, examples, or important explanations
4. Write in {language_name}
5. Keep descriptions concise (10-15 words max)

Format your response as:
[MM:SS] Brief description
[MM:SS] Brief description
[MM:SS] Brief description

Important timestamps:"""


def parse_timestamps_response(response: str) -> List[Dict]:
    """
    Parse timestamps from Ollama response.
    
    Args:
        response: Raw response from Ollama
        
    Returns:
        List of timestamp dictionaries
    """
    timestamps = []
    lines = response.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Match [MM:SS] pattern
        match = re.match(r'\[(\d+):(\d{2})\]\s*(.+)', line)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            description = match.group(3).strip()
            
            total_seconds = minutes * 60 + seconds
            timestamps.append({
                "time": total_seconds,
                "formatted": f"{minutes}:{seconds:02d}",
                "description": description
            })
    
    return timestamps


def summarize_video(transcript: Dict, metadata: Dict, model: str = "gemma3:12b", output_dir: str = None) -> Dict:
    """
    Summarize video transcript using Ollama.
    
    Args:
        transcript: Transcript data from transcriber
        metadata: Video metadata from downloader
        model: Ollama model to use
        output_dir: Directory to save intermediate files
        
    Returns:
        Summary data for markdown generation
    """
    print("Generating video summary...")
    
    segments = transcript["segments"]
    full_text = transcript["full_text"]
    language = transcript["language"]
    chapters = metadata.get("chapters", [])
    video_title = metadata["title"]
    video_url = metadata["url"]
    duration = metadata["duration"]
    
    summary_data = {
        "video_title": video_title,
        "video_url": video_url,
        "duration": duration,
        "language": language,
        "uploader": metadata.get("uploader", "Unknown"),
        "chapters": []
    }
    
    # Save intermediate files
    if output_dir:
        # Save raw transcript
        with open(os.path.join(output_dir, "transcript.json"), 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        with open(os.path.join(output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    if chapters:
        # Process each chapter
        print(f"Processing {len(chapters)} chapters...")
        
        for i, chapter in enumerate(chapters):
            print(f"  Chapter {i+1}: {chapter['title']}")
            
            # Extract text for this chapter
            chapter_text = extract_text_for_timerange(
                segments, chapter["start"], chapter["end"]
            )
            
            if not chapter_text.strip():
                print(f"    Warning: No text found for chapter {i+1}")
                continue
            
            # Generate chapter summary
            summary_prompt = create_chapter_summary_prompt(
                chapter["title"], chapter_text, language, segments, chapter["start"], chapter["end"]
            )
            chapter_summary = call_ollama(summary_prompt, model)
            
            # Generate timestamps
            timestamps_prompt = create_timestamps_prompt(
                chapter["title"], chapter_text, segments, 
                chapter["start"], chapter["end"], language
            )
            timestamps_response = call_ollama(timestamps_prompt, model, temperature=0.5)
            timestamps = parse_timestamps_response(timestamps_response)
            
            # Create chapter data
            chapter_data = {
                "title": chapter["title"],
                "start": chapter["start"],
                "end": chapter["end"],
                "summary": chapter_summary,
                "timestamps": timestamps,
                "text": chapter_text
            }
            
            summary_data["chapters"].append(chapter_data)
            
            # Save individual chapter summary
            if output_dir:
                chapter_file = os.path.join(output_dir, f"chapter_{i+1}_summary.json")
                with open(chapter_file, 'w', encoding='utf-8') as f:
                    json.dump(chapter_data, f, indent=2, ensure_ascii=False)
    
    else:
        # Process entire video as one piece
        print("Processing entire video (no chapters)...")
        
        # Generate full video summary
        summary_prompt = create_full_video_summary_prompt(
            video_title, full_text, language, segments, duration
        )
        full_summary = call_ollama(summary_prompt, model)
        
        # Generate timestamps for entire video
        timestamps_prompt = create_timestamps_prompt(
            video_title, full_text, segments, 0, duration, language
        )
        timestamps_response = call_ollama(timestamps_prompt, model, temperature=0.5)
        timestamps = parse_timestamps_response(timestamps_response)
        
        # Create single chapter data
        chapter_data = {
            "title": "Full Video",
            "start": 0,
            "end": duration,
            "summary": full_summary,
            "timestamps": timestamps,
            "text": full_text
        }
        
        summary_data["chapters"].append(chapter_data)
        
        # Save full video summary
        if output_dir:
            full_summary_file = os.path.join(output_dir, "full_video_summary.json")
            with open(full_summary_file, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=2, ensure_ascii=False)
    
    # Save complete summary data
    if output_dir:
        summary_file = os.path.join(output_dir, "summary_data.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print("✓ Summary generation complete")
    return summary_data
