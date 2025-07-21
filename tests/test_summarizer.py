"""
Unit tests for the summarizer module.
"""

import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import pytest

from ytldr.summarizer import (
    call_ollama,
    extract_text_for_timerange,
    create_chapter_summary_prompt,
    create_full_video_summary_prompt,
    create_timestamps_prompt,
    parse_timestamps_response,
    summarize_video
)


class TestSummarizer:
    """Test cases for summarizer functions."""

    @pytest.mark.unit
    def test_extract_text_for_timerange(self):
        """Test text extraction for specific time ranges."""
        segments = [
            {"start": 0, "end": 10, "text": "Hello world"},
            {"start": 10, "end": 20, "text": "This is a test"},
            {"start": 20, "end": 30, "text": "End of test"}
        ]
        
        # Test exact range
        result = extract_text_for_timerange(segments, 0, 30)
        assert result == "Hello world This is a test End of test"
        
        # Test partial range - segments that start within the range
        result = extract_text_for_timerange(segments, 5, 25)
        assert result == "This is a test"
        
        # Test empty range
        result = extract_text_for_timerange(segments, 50, 60)
        assert result == ""

    @pytest.mark.unit
    def test_create_chapter_summary_prompt(self):
        """Test chapter summary prompt creation."""
        segments = [
            {"start": 0, "end": 10, "text": "First segment"},
            {"start": 10, "end": 20, "text": "Second segment"}
        ]
        
        prompt = create_chapter_summary_prompt(
            "Test Chapter", 
            "This is test content", 
            "en",
            segments,
            0,
            20
        )
        
        assert "Test Chapter" in prompt
        assert "English" in prompt
        assert "comprehensive summary" in prompt
        assert "full sentences" in prompt
        assert "timestamp" in prompt.lower()
        assert "[0:00]" in prompt
        assert "[0:10]" in prompt

    @pytest.mark.unit
    def test_create_full_video_summary_prompt(self):
        """Test full video summary prompt creation."""
        segments = [
            {"start": 0, "end": 10, "text": "First segment"},
            {"start": 10, "end": 20, "text": "Second segment"}
        ]
        
        prompt = create_full_video_summary_prompt(
            "Test Video", 
            "This is full video content", 
            "es",
            segments,
            20
        )
        
        assert "Test Video" in prompt
        assert "Spanish" in prompt
        assert "500-800 words" in prompt
        assert "timestamp" in prompt.lower()
        assert "[0:00]" in prompt
        assert "[0:10]" in prompt

    @pytest.mark.unit
    def test_create_timestamps_prompt(self):
        """Test timestamp prompt creation."""
        segments = [
            {"start": 0, "end": 10, "text": "First segment"},
            {"start": 10, "end": 20, "text": "Second segment"}
        ]
        
        prompt = create_timestamps_prompt(
            "Test Chapter",
            "Test content",
            segments,
            0,
            20,
            "en"
        )
        
        assert "Test Chapter" in prompt
        assert "[0:00]" in prompt
        assert "[0:10]" in prompt
        assert "3-5 key timestamps" in prompt

    @pytest.mark.unit
    def test_parse_timestamps_response_valid(self):
        """Test parsing valid timestamp responses."""
        response = """
        [0:15] Introduction to the topic
        [2:30] Key concept explanation
        [5:45] Important demonstration
        """
        
        timestamps = parse_timestamps_response(response)
        
        assert len(timestamps) == 3
        assert timestamps[0]["time"] == 15
        assert timestamps[0]["formatted"] == "0:15"
        assert timestamps[0]["description"] == "Introduction to the topic"
        assert timestamps[1]["time"] == 150
        assert timestamps[2]["time"] == 345

    @pytest.mark.unit
    def test_parse_timestamps_response_invalid(self):
        """Test parsing invalid timestamp responses."""
        response = """
        Invalid format
        [1:30] Valid timestamp
        Another invalid line
        [2:45] Another valid one
        """
        
        timestamps = parse_timestamps_response(response)
        
        assert len(timestamps) == 2
        assert timestamps[0]["time"] == 90
        assert timestamps[1]["time"] == 165

    @pytest.mark.unit
    def test_parse_timestamps_response_empty(self):
        """Test parsing empty timestamp response."""
        timestamps = parse_timestamps_response("")
        assert timestamps == []
        
        timestamps = parse_timestamps_response("No timestamps here")
        assert timestamps == []

    @pytest.mark.unit
    @patch('ytldr.summarizer.requests.post')
    def test_call_ollama_success(self, mock_post):
        """Test successful Ollama API call."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Test response"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = call_ollama("Test prompt", "gemma3:12b")
        
        assert result == "Test response"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['model'] == "gemma3:12b"
        assert call_args[1]['json']['prompt'] == "Test prompt"

    @pytest.mark.unit
    @patch('ytldr.summarizer.requests.post')
    def test_call_ollama_failure(self, mock_post):
        """Test Ollama API call failure."""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException("Connection failed")
        
        with pytest.raises(Exception, match="Failed to call Ollama: Connection failed"):
            call_ollama("Test prompt")

    @pytest.mark.unit
    @patch('ytldr.summarizer.call_ollama')
    def test_summarize_video_with_chapters(self, mock_call_ollama):
        """Test video summarization with chapters."""
        # Mock Ollama responses
        mock_call_ollama.side_effect = [
            "Chapter 1 summary content",
            "[0:15] Key moment 1\n[2:30] Key moment 2",
            "Chapter 2 summary content", 
            "[5:45] Key moment 3\n[8:20] Key moment 4"
        ]
        
        transcript = {
            "segments": [
                {"start": 0, "end": 10, "text": "Chapter 1 content"},
                {"start": 10, "end": 20, "text": "Chapter 2 content"}
            ],
            "full_text": "Full video content",
            "language": "en"
        }
        
        metadata = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=test",
            "duration": 20,
            "chapters": [
                {"start": 0, "end": 10, "title": "Chapter 1"},
                {"start": 10, "end": 20, "title": "Chapter 2"}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = summarize_video(transcript, metadata, "gemma3:12b", temp_dir)
            
            assert result["video_title"] == "Test Video"
            assert result["language"] == "en"
            assert len(result["chapters"]) == 2
            
            # Check chapter data
            assert result["chapters"][0]["title"] == "Chapter 1"
            assert result["chapters"][0]["summary"] == "Chapter 1 summary content"
            assert len(result["chapters"][0]["timestamps"]) == 2
            
            # Check if files were created
            files = os.listdir(temp_dir)
            assert "transcript.json" in files
            assert "metadata.json" in files
            assert "summary_data.json" in files
            assert "chapter_1_summary.json" in files
            assert "chapter_2_summary.json" in files

    @pytest.mark.unit
    @patch('ytldr.summarizer.call_ollama')
    def test_summarize_video_without_chapters(self, mock_call_ollama):
        """Test video summarization without chapters."""
        # Mock Ollama responses
        mock_call_ollama.side_effect = [
            "Full video summary content",
            "[0:15] Key moment 1\n[2:30] Key moment 2"
        ]
        
        transcript = {
            "segments": [
                {"start": 0, "end": 20, "text": "Full video content"}
            ],
            "full_text": "Full video content",
            "language": "en"
        }
        
        metadata = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=test",
            "duration": 20,
            "chapters": []
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = summarize_video(transcript, metadata, "gemma3:12b", temp_dir)
            
            assert result["video_title"] == "Test Video"
            assert len(result["chapters"]) == 1
            assert result["chapters"][0]["title"] == "Full Video"
            assert result["chapters"][0]["summary"] == "Full video summary content"
            
            # Check if files were created
            files = os.listdir(temp_dir)
            assert "full_video_summary.json" in files

    @pytest.mark.unit
    @patch('ytldr.summarizer.call_ollama')
    def test_summarize_video_no_output_dir(self, mock_call_ollama):
        """Test video summarization without output directory."""
        mock_call_ollama.side_effect = [
            "Chapter summary content",
            "[0:15] Key moment"
        ]
        
        transcript = {
            "segments": [{"start": 0, "end": 10, "text": "Content"}],
            "full_text": "Content",
            "language": "en"
        }
        
        metadata = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=test",
            "duration": 10,
            "chapters": [{"start": 0, "end": 10, "title": "Chapter 1"}]
        }
        
        result = summarize_video(transcript, metadata, "gemma3:12b")
        
        assert result["video_title"] == "Test Video"
        assert len(result["chapters"]) == 1

    @pytest.mark.unit
    @patch('ytldr.summarizer.call_ollama')
    def test_summarize_video_empty_chapter(self, mock_call_ollama):
        """Test handling of empty chapter content."""
        # Mock Ollama responses for the chapter that has content
        mock_call_ollama.side_effect = [
            "Chapter 1 summary content",
            "[0:15] Key moment"
        ]
        
        transcript = {
            "segments": [{"start": 0, "end": 10, "text": "Content"}],
            "full_text": "Content",
            "language": "en"
        }
        
        metadata = {
            "title": "Test Video",
            "url": "https://youtube.com/watch?v=test",
            "duration": 20,
            "chapters": [
                {"start": 0, "end": 10, "title": "Chapter 1"},
                {"start": 15, "end": 20, "title": "Chapter 2"}  # No content in this range
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = summarize_video(transcript, metadata, "gemma3:12b", temp_dir)
            
            # Should only have one chapter (the one with content)
            assert len(result["chapters"]) == 1
            assert result["chapters"][0]["title"] == "Chapter 1" 