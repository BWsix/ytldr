"""
Integration tests for the complete ytldr pipeline.
"""

import tempfile
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ytldr.downloader import download_video, get_metadata
from ytldr.transcriber import transcribe_audio
from ytldr.summarizer import summarize_video
from ytldr.utils import generate_markdown, save_markdown


class TestIntegration:
    """Integration tests for the complete pipeline."""

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('ytldr.downloader.yt_dlp.YoutubeDL')
    @patch('ytldr.transcriber.whisper.load_model')
    @patch('ytldr.summarizer.call_ollama')
    def test_complete_pipeline_with_chapters(self, mock_call_ollama, mock_whisper_model, mock_ydl):
        """Test complete pipeline with a video that has chapters."""
        
        # Mock yt-dlp responses
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock video info
        mock_video_info = {
            'title': 'Test Video with Chapters',
            'description': 'Test description',
            'duration': 120,
            'uploader': 'Test Uploader',
            'chapters': [
                {'start_time': 0, 'end_time': 60, 'title': 'Introduction'},
                {'start_time': 60, 'end_time': 120, 'title': 'Main Content'}
            ]
        }
        mock_ydl_instance.extract_info.return_value = mock_video_info
        
        # Mock Whisper transcription
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        mock_model.transcribe.return_value = {
            'text': 'This is a test transcript with multiple segments.',
            'language': 'en',
            'segments': [
                {'start': 0, 'end': 30, 'text': 'This is a test'},
                {'start': 30, 'end': 60, 'text': 'transcript with multiple'},
                {'start': 60, 'end': 90, 'text': 'segments for chapter 2'},
                {'start': 90, 'end': 120, 'text': 'and more content.'}
            ]
        }
        
        # Mock Ollama responses
        mock_call_ollama.side_effect = [
            "Introduction chapter summary content",
            "[0:15] Key introduction moment\n[0:30] Another important point",
            "Main content chapter summary content",
            "[1:05] Key main content moment\n[1:30] Final important point"
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Download video
            metadata = download_video("https://youtube.com/watch?v=test", str(temp_path))
            
            assert metadata['title'] == 'Test Video with Chapters'
            assert len(metadata['chapters']) == 2
            assert metadata['chapters'][0]['title'] == 'Introduction'
            
            # Step 2: Transcribe audio
            # Create a dummy audio file
            audio_file = temp_path / "audio.mp3"
            audio_file.write_text("dummy audio content")
            metadata['audio_file'] = str(audio_file)
            
            transcript = transcribe_audio(str(audio_file), str(temp_path))
            
            assert transcript['language'] == 'en'
            assert len(transcript['segments']) == 4
            assert 'test transcript' in transcript['full_text']
            
            # Step 3: Generate summary
            summary_data = summarize_video(transcript, metadata, "gemma3:12b", str(temp_path))
            
            assert summary_data['video_title'] == 'Test Video with Chapters'
            assert len(summary_data['chapters']) == 2
            assert summary_data['chapters'][0]['title'] == 'Introduction'
            assert summary_data['chapters'][1]['title'] == 'Main Content'
            
            # Step 4: Generate markdown
            markdown = generate_markdown(summary_data)
            
            assert "# Test Video with Chapters" in markdown
            assert "**Chapters:** 2" in markdown
            assert "## Chapter Summaries" in markdown
            assert "Introduction chapter summary content" in markdown
            assert "Main content chapter summary content" in markdown
            
            # Step 5: Save markdown
            output_file = temp_path / "summary.md"
            save_markdown(markdown, str(output_file))
            
            assert output_file.exists()
            
            # Check generated files
            files = list(temp_path.glob("*"))
            file_names = [f.name for f in files]
            
            assert "video_metadata.json" in file_names
            assert "transcript.json" in file_names
            assert "transcript.txt" in file_names
            assert "summary_data.json" in file_names
            assert "chapter_1_summary.json" in file_names
            assert "chapter_2_summary.json" in file_names
            assert "summary.md" in file_names

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('ytldr.downloader.yt_dlp.YoutubeDL')
    @patch('ytldr.transcriber.whisper.load_model')
    @patch('ytldr.summarizer.call_ollama')
    def test_complete_pipeline_without_chapters(self, mock_call_ollama, mock_whisper_model, mock_ydl):
        """Test complete pipeline with a video that has no chapters."""
        
        # Mock yt-dlp responses
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock video info without chapters
        mock_video_info = {
            'title': 'Test Video without Chapters',
            'description': 'Test description',
            'duration': 180,
            'uploader': 'Test Uploader',
            'chapters': []
        }
        mock_ydl_instance.extract_info.return_value = mock_video_info
        
        # Mock Whisper transcription
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        mock_model.transcribe.return_value = {
            'text': 'This is a longer test transcript for a video without chapters.',
            'language': 'en',
            'segments': [
                {'start': 0, 'end': 30, 'text': 'This is a longer test'},
                {'start': 30, 'end': 60, 'text': 'transcript for a video'},
                {'start': 60, 'end': 90, 'text': 'without chapters.'}
            ]
        }
        
        # Mock Ollama responses
        mock_call_ollama.side_effect = [
            "Full video summary content with comprehensive details about the topic.",
            "[0:30] Key moment in the video\n[1:00] Another important timestamp\n[1:30] Final key point"
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Step 1: Download video
            metadata = download_video("https://youtube.com/watch?v=test", str(temp_path))
            
            assert metadata['title'] == 'Test Video without Chapters'
            assert len(metadata['chapters']) == 0
            
            # Step 2: Transcribe audio
            audio_file = temp_path / "audio.mp3"
            audio_file.write_text("dummy audio content")
            metadata['audio_file'] = str(audio_file)
            
            transcript = transcribe_audio(str(audio_file), str(temp_path))
            
            assert transcript['language'] == 'en'
            assert 'longer test transcript' in transcript['full_text']
            
            # Step 3: Generate summary
            summary_data = summarize_video(transcript, metadata, "gemma3:12b", str(temp_path))
            
            assert summary_data['video_title'] == 'Test Video without Chapters'
            assert len(summary_data['chapters']) == 1
            assert summary_data['chapters'][0]['title'] == 'Full Video'
            
            # Step 4: Generate markdown
            markdown = generate_markdown(summary_data)
            
            assert "# Test Video without Chapters" in markdown
            assert "**Chapters:** None" in markdown
            assert "## Summary" in markdown
            assert "Full video summary content" in markdown
            assert "## Important Timestamps" in markdown
            
            # Step 5: Save markdown
            output_file = temp_path / "summary.md"
            save_markdown(markdown, str(output_file))
            
            assert output_file.exists()
            
            # Check generated files
            files = list(temp_path.glob("*"))
            file_names = [f.name for f in files]
            
            assert "full_video_summary.json" in file_names
            assert "summary.md" in file_names

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('ytldr.downloader.yt_dlp.YoutubeDL')
    @patch('ytldr.transcriber.whisper.load_model')
    @patch('ytldr.summarizer.call_ollama')
    def test_pipeline_with_different_language(self, mock_call_ollama, mock_whisper_model, mock_ydl):
        """Test pipeline with non-English content."""
        
        # Mock yt-dlp responses
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        mock_video_info = {
            'title': 'Vidéo de Test en Français',
            'description': 'Description en français',
            'duration': 90,
            'uploader': 'Test Uploader',
            'chapters': []
        }
        mock_ydl_instance.extract_info.return_value = mock_video_info
        
        # Mock Whisper transcription in French
        mock_model = MagicMock()
        mock_whisper_model.return_value = mock_model
        mock_model.transcribe.return_value = {
            'text': 'Ceci est un transcript de test en français.',
            'language': 'fr',
            'segments': [
                {'start': 0, 'end': 30, 'text': 'Ceci est un transcript'},
                {'start': 30, 'end': 60, 'text': 'de test en français.'}
            ]
        }
        
        # Mock Ollama responses in French
        mock_call_ollama.side_effect = [
            "Résumé complet de la vidéo en français avec tous les détails importants.",
            "[0:30] Moment clé dans la vidéo\n[1:00] Autre point important"
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Run pipeline
            metadata = download_video("https://youtube.com/watch?v=test", str(temp_path))
            
            audio_file = temp_path / "audio.mp3"
            audio_file.write_text("dummy audio content")
            metadata['audio_file'] = str(audio_file)
            
            transcript = transcribe_audio(str(audio_file), str(temp_path))
            summary_data = summarize_video(transcript, metadata, "gemma3:12b", str(temp_path))
            markdown = generate_markdown(summary_data)
            
            # Verify language handling
            assert summary_data['language'] == 'fr'
            assert "**Language:** French" in markdown
            assert "Résumé complet" in markdown

    @pytest.mark.integration
    @pytest.mark.slow
    @patch('ytldr.downloader.yt_dlp.YoutubeDL')
    @patch('ytldr.transcriber.whisper.load_model')
    @patch('ytldr.summarizer.call_ollama')
    def test_pipeline_error_handling(self, mock_call_ollama, mock_whisper_model, mock_ydl):
        """Test pipeline error handling."""
        
        # Mock yt-dlp to raise an exception
        mock_ydl.side_effect = Exception("Download failed")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Should raise an exception
            with pytest.raises(Exception, match="Download failed"):
                download_video("https://youtube.com/watch?v=test", str(temp_path))

    @pytest.mark.integration
    @pytest.mark.slow
    def test_markdown_content_structure(self):
        """Test that generated markdown has proper structure."""
        
        # Create test summary data
        summary_data = {
            "video_title": "Comprehensive Test Video",
            "video_url": "https://youtube.com/watch?v=comprehensive",
            "duration": 3600,  # 1 hour
            "language": "en",
            "chapters": [
                {
                    "title": "Introduction",
                    "start": 0,
                    "end": 600,
                    "summary": "This chapter introduces the main concepts and provides an overview of what will be covered in the video.",
                    "timestamps": [
                        {"time": 30, "formatted": "0:30", "description": "Overview of topics"},
                        {"time": 120, "formatted": "2:00", "description": "Key concept introduction"}
                    ]
                },
                {
                    "title": "Deep Dive",
                    "start": 600,
                    "end": 1800,
                    "summary": "This chapter goes into detailed explanations and provides practical examples of the concepts introduced earlier.",
                    "timestamps": [
                        {"time": 720, "formatted": "12:00", "description": "Detailed explanation starts"},
                        {"time": 1200, "formatted": "20:00", "description": "Practical example"},
                        {"time": 1500, "formatted": "25:00", "description": "Advanced concepts"}
                    ]
                },
                {
                    "title": "Conclusion",
                    "start": 1800,
                    "end": 3600,
                    "summary": "This chapter wraps up the discussion and provides final thoughts and recommendations.",
                    "timestamps": [
                        {"time": 2400, "formatted": "40:00", "description": "Summary of key points"},
                        {"time": 3000, "formatted": "50:00", "description": "Final recommendations"}
                    ]
                }
            ]
        }
        
        # Generate markdown
        markdown = generate_markdown(summary_data)
        
        # Test structure
        lines = markdown.split('\n')
        
        # Check header
        assert lines[0] == "# Comprehensive Test Video"
        assert "**Duration:** 1:00:00" in lines[2]
        assert "**Language:** English" in lines[2]
        assert "**Chapters:** 3" in lines[2]
        
        # Check chapter structure
        assert "## Chapter Summaries" in markdown
        assert "### Introduction" in markdown
        assert "### Deep Dive" in markdown
        assert "### Conclusion" in markdown
        
        # Check timestamps
        assert "[0:30](https://youtube.com/watch?v=comprehensive&t=30s)" in markdown
        assert "[12:00](https://youtube.com/watch?v=comprehensive&t=720s)" in markdown
        assert "[40:00](https://youtube.com/watch?v=comprehensive&t=2400s)" in markdown
        
        # Check footer
        assert "*Generated by ytldr" in markdown
        assert "Model: gemma3:12b" in markdown 