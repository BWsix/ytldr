"""
Utility functions for formatting and markdown generation.
"""

import os
import re
from typing import Dict, List
from datetime import datetime


def sanitize_title_for_directory(title: str) -> str:
    """
    Sanitize video title for use as directory name.
    
    Args:
        title: Original video title
        
    Returns:
        Sanitized directory name
    """
    # Replace non-alphanumeric characters with underscores
    sanitized = re.sub(r'[^\w\-_.]', '_', title)
    # Replace multiple consecutive underscores with single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    # Fallback if title becomes empty
    if not sanitized:
        sanitized = "video"
    return sanitized


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
    else:
        return f"{minutes}:{remaining_seconds:02d}"


def create_youtube_timestamp_link(video_url: str, seconds: int) -> str:
    """
    Create a YouTube timestamp link.
    
    Args:
        video_url: Base YouTube URL
        seconds: Time in seconds
        
    Returns:
        Markdown link with timestamp
    """
    timestamp = format_duration(seconds)
    timestamp_url = f"{video_url}&t={seconds}s"
    return f"[{timestamp}]({timestamp_url})"


def process_inline_timestamps(summary_text: str, video_url: str) -> str:
    """
    Process summary text and convert timestamp references to YouTube links.
    
    Args:
        summary_text: Summary text that may contain timestamp references like [2:15]
        video_url: Base YouTube URL
        
    Returns:
        Processed text with timestamp links
    """
    # Pattern to match [MM:SS] or [M:SS] format
    timestamp_pattern = r'\[(\d+):(\d{2})\]'
    
    def replace_timestamp(match):
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        total_seconds = minutes * 60 + seconds
        timestamp = f"{minutes}:{seconds:02d}"
        timestamp_url = f"{video_url}&t={total_seconds}s"
        return f"[{timestamp}]({timestamp_url})"
    
    return re.sub(timestamp_pattern, replace_timestamp, summary_text)


def generate_table_of_contents(chapters: List[Dict], video_url: str) -> str:
    """
    Generate a table of contents for the markdown document.
    
    Args:
        chapters: List of chapter data
        video_url: Base YouTube URL
        
    Returns:
        Table of contents markdown string
    """
    toc = "## Table of Contents\n\n"
    
    # Always include main sections
    toc += "- [Video Information](#video-information)\n"
    toc += "- [Summary](#summary)\n"
    
    if len(chapters) == 1 and chapters[0]["title"] == "Full Video":
        # Single chapter - add important timestamps if available
        if chapters[0]["timestamps"]:
            toc += "- [Important Timestamps](#important-timestamps)\n"
    else:
        # Multiple chapters
        toc += "- [Chapter Summaries](#chapter-summaries)\n"
        
        # Add chapter entries
        for i, chapter in enumerate(chapters):
            start_time = int(chapter["start"])
            end_time = int(chapter["end"])
            chapter_title = chapter["title"]
            
            # Create anchor-friendly chapter title
            anchor = f"{i+1}-{format_duration(start_time)}-{format_duration(end_time)}-{chapter_title.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')}"
            anchor = re.sub(r'[^\w\-]', '', anchor)
            
            # Create standard markdown anchor from chapter title only
            anchor = re.sub(r'[^\w\-]', '-', chapter_title.lower()).replace('--', '-').strip('-')
            toc += f"  - [{chapter_title}](#{anchor})\n"
    
    toc += "\n"
    return toc


def generate_markdown(summary_data: Dict) -> str:
    """
    Generate markdown summary from summary data.
    
    Args:
        summary_data: Summary data from summarizer
        
    Returns:
        Formatted markdown string
    """
    video_title = summary_data["video_title"]
    video_url = summary_data["video_url"]
    duration = summary_data["duration"]
    language = summary_data["language"]
    chapters = summary_data["chapters"]
    uploader = summary_data.get("uploader", "Unknown")
    
    # Get language name
    language_name = {"en": "English", "es": "Spanish", "fr": "French", "de": "German", 
                    "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese", 
                    "ko": "Korean", "zh": "Chinese"}.get(language, "English")
    
    # Header
    markdown = f"# {video_title}\n\n"
    markdown += f"**Duration:** {format_duration(duration)} | **Language:** {language_name}"
    
    if len(chapters) > 1:
        markdown += f" | **Chapters:** {len(chapters)}"
    else:
        markdown += " | **Chapters:** None"
    
    markdown += "\n\n"
    
    # Generate and add Table of Contents
    markdown += generate_table_of_contents(chapters, video_url)
    
    # Video information section
    markdown += "## Video Information\n\n"
    markdown += f"**Channel:** {uploader}\n"
    markdown += f"**Original URL:** [{video_url}]({video_url})\n\n"
    
    # Summary section
    if len(chapters) == 1 and chapters[0]["title"] == "Full Video":
        # Single chapter (no chapters in video)
        chapter = chapters[0]
        markdown += "## Summary\n\n"
        # Process inline timestamps in the summary
        processed_summary = process_inline_timestamps(chapter['summary'], video_url)
        markdown += f"{processed_summary}\n\n"
        
        # Important timestamps (keep for reference)
        if chapter["timestamps"]:
            markdown += "## Important Timestamps\n\n"
            for ts in chapter["timestamps"]:
                timestamp_link = create_youtube_timestamp_link(video_url, ts["time"])
                markdown += f"- **{timestamp_link}** - {ts['description']}\n"
            markdown += "\n"
    
    else:
        # Multiple chapters
        markdown += "## Summary\n\n"
        markdown += f"This comprehensive video covers multiple topics with detailed explanations and practical examples.\n\n"
        
        markdown += "## Chapter Summaries\n\n"
        
        for i, chapter in enumerate(chapters):
            # Chapter header with time range and anchor
            start_time = int(chapter["start"])
            end_time = int(chapter["end"])
            chapter_title = chapter["title"]
            
            # Create anchor-friendly chapter title
            anchor = f"{i+1}-{format_duration(start_time)}-{format_duration(end_time)}-{chapter_title.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')}"
            anchor = re.sub(r'[^\w\-]', '', anchor)
            
            markdown += f"### {chapter['title']}\n\n"
            
            # YouTube link with timestamp
            chapter_start_link = create_youtube_timestamp_link(video_url, start_time)
            markdown += f"**Link:** {chapter_start_link}\n\n"
            
            # Important timestamps for this chapter
            if chapter["timestamps"]:
                markdown += "**Important Moments:**\n"
                for ts in chapter["timestamps"]:
                    timestamp_link = create_youtube_timestamp_link(video_url, ts["time"])
                    markdown += f"- **{timestamp_link}** - {ts['description']}\n"
                markdown += "\n"
            
            # Process inline timestamps in the chapter summary
            processed_summary = process_inline_timestamps(chapter['summary'], video_url)
            markdown += f"{processed_summary}\n\n"
    
    # Footer
    markdown += "---\n\n"
    markdown += f"*Generated by ytldr | Model: gemma3:12b | Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return markdown


def save_markdown(markdown: str, output_file: str):
    """
    Save markdown content to file.
    
    Args:
        markdown: Markdown content
        output_file: Output file path
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown) 