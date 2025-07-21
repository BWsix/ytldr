"""
Video downloader module for YouTube videos.
Handles downloading audio and extracting metadata.
"""

import json
import os
from typing import Dict, List, Optional
import yt_dlp


def get_metadata(url: str) -> Dict:
    """
    Get metadata for a YouTube video.
    """
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


def download_video(url: str, output_dir: str) -> Dict:
    """
    Download video as audio and extract metadata.
    
    Args:
        url: YouTube URL
        output_dir: Directory to save files
        
    Returns:
        Dict containing metadata and file paths
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Configure yt-dlp for audio-only download
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'writesubtitles': False,
        'writeautomaticsub': False,
        'extract_flat': False,
    }
    
    metadata = {}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract info first
        info = ydl.extract_info(url, download=False)
        
        # Store basic metadata with proper fallbacks
        metadata['title'] = info.get('title') or 'Unknown Title'
        metadata['description'] = info.get('description') or ''
        metadata['duration'] = info.get('duration') or 0
        metadata['uploader'] = info.get('uploader') or 'Unknown'
        metadata['url'] = url
        
        # Extract chapters if available
        chapters = info.get('chapters', [])
        if chapters:
            metadata['chapters'] = [
                {
                    'start': chapter.get('start_time', 0),
                    'end': chapter.get('end_time', 0),
                    'title': chapter.get('title', f'Chapter {i+1}')
                }
                for i, chapter in enumerate(chapters)
            ]
        else:
            metadata['chapters'] = []
        
        # Download the audio
        ydl.download([url])
    
    # Find the downloaded audio file
    audio_file = None
    for file in os.listdir(output_dir):
        if file.startswith('audio.') and file.endswith('.mp3'):
            audio_file = os.path.join(output_dir, file)
            break
    
    metadata['audio_file'] = audio_file
    
    # Save metadata
    metadata_file = os.path.join(output_dir, 'video_metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return metadata 