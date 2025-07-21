"""
Unit tests for utility functions.
"""

import os
import tempfile
import pytest

from ytldr.utils import (
    sanitize_title_for_directory,
    format_duration,
    create_youtube_timestamp_link,
    process_inline_timestamps,
    generate_table_of_contents,
    generate_markdown,
    save_markdown
)


class TestUtils:
    """Test cases for utility functions."""

    @pytest.mark.unit
    def test_sanitize_title_for_directory(self):
        """Test title sanitization for directory names."""
        # Test normal title
        assert sanitize_title_for_directory("Hello World") == "Hello_World"
        
        # Test with special characters
        assert sanitize_title_for_directory("Video: Test & Demo!") == "Video_Test_Demo"
        
        # Test with multiple spaces
        assert sanitize_title_for_directory("Multiple   Spaces") == "Multiple_Spaces"
        
        # Test with leading/trailing spaces
        assert sanitize_title_for_directory("  Trimmed  ") == "Trimmed"
        
        # Test empty string
        assert sanitize_title_for_directory("") == "video"
        
        # Test with only special characters
        assert sanitize_title_for_directory("!@#$%") == "video"

    @pytest.mark.unit
    def test_format_duration(self):
        """Test duration formatting."""
        # Test seconds only
        assert format_duration(45) == "0:45"
        
        # Test minutes and seconds
        assert format_duration(125) == "2:05"
        
        # Test hours, minutes, and seconds
        assert format_duration(3661) == "1:01:01"
        
        # Test zero
        assert format_duration(0) == "0:00"

    @pytest.mark.unit
    def test_create_youtube_timestamp_link(self):
        """Test YouTube timestamp link creation."""
        url = "https://www.youtube.com/watch?v=test123"
        
        # Test seconds only
        link = create_youtube_timestamp_link(url, 45)
        assert link == "[0:45](https://www.youtube.com/watch?v=test123&t=45s)"
        
        # Test minutes and seconds
        link = create_youtube_timestamp_link(url, 125)
        assert link == "[2:05](https://www.youtube.com/watch?v=test123&t=125s)"
        
        # Test hours, minutes, and seconds
        link = create_youtube_timestamp_link(url, 3661)
        assert link == "[1:01:01](https://www.youtube.com/watch?v=test123&t=3661s)"

    @pytest.mark.unit
    def test_process_inline_timestamps(self):
        """Test processing inline timestamp references."""
        video_url = "https://www.youtube.com/watch?v=test123"
        
        # Test single timestamp
        text = "The speaker introduces the concept [2:15] and explains it."
        result = process_inline_timestamps(text, video_url)
        expected = "The speaker introduces the concept [2:15](https://www.youtube.com/watch?v=test123&t=135s) and explains it."
        assert result == expected
        
        # Test multiple timestamps
        text = "First concept [1:30], then second [3:45], and finally [5:20]."
        result = process_inline_timestamps(text, video_url)
        assert "[1:30](https://www.youtube.com/watch?v=test123&t=90s)" in result
        assert "[3:45](https://www.youtube.com/watch?v=test123&t=225s)" in result
        assert "[5:20](https://www.youtube.com/watch?v=test123&t=320s)" in result
        
        # Test no timestamps
        text = "This text has no timestamps."
        result = process_inline_timestamps(text, video_url)
        assert result == text
        
        # Test invalid timestamp format (should be ignored)
        text = "Invalid [2:15:30] and valid [2:15] timestamps."
        result = process_inline_timestamps(text, video_url)
        assert "[2:15:30]" in result  # Should remain unchanged
        assert "[2:15](https://www.youtube.com/watch?v=test123&t=135s)" in result

    @pytest.mark.unit
    def test_generate_table_of_contents_single_chapter(self):
        """Test table of contents generation for single chapter video."""
        chapters = [
            {
                "title": "Full Video",
                "start": 0,
                "end": 120,
                "timestamps": [
                    {"time": 90, "formatted": "1:30", "description": "Key moment 1"},
                    {"time": 165, "formatted": "2:45", "description": "Key moment 2"}
                ]
            }
        ]
        
        toc = generate_table_of_contents(chapters, "https://youtube.com/watch?v=test")
        
        assert "## Table of Contents" in toc
        assert "- [Video Information](#video-information)" in toc
        assert "- [Summary](#summary)" in toc
        assert "- [Important Timestamps](#important-timestamps)" in toc
        assert "## Chapter Summaries" not in toc

    @pytest.mark.unit
    def test_generate_table_of_contents_multiple_chapters(self):
        """Test table of contents generation for multi-chapter video."""
        chapters = [
            {
                "title": "Introduction",
                "start": 0,
                "end": 150,
                "timestamps": []
            },
            {
                "title": "Main Content",
                "start": 150,
                "end": 300,
                "timestamps": []
            }
        ]
        
        toc = generate_table_of_contents(chapters, "https://youtube.com/watch?v=test")
        
        assert "## Table of Contents" in toc
        assert "- [Video Information](#video-information)" in toc
        assert "- [Summary](#summary)" in toc
        assert "- [Chapter Summaries](#chapter-summaries)" in toc
        assert "  - [Introduction](#introduction)" in toc
        assert "  - [Main Content](#main-content)" in toc
        assert "- [Important Timestamps](#important-timestamps)" not in toc

    @pytest.mark.unit
    def test_generate_table_of_contents_single_chapter_no_timestamps(self):
        """Test table of contents generation for single chapter without timestamps."""
        chapters = [
            {
                "title": "Full Video",
                "start": 0,
                "end": 120,
                "timestamps": []
            }
        ]
        
        toc = generate_table_of_contents(chapters, "https://youtube.com/watch?v=test")
        
        assert "## Table of Contents" in toc
        assert "- [Video Information](#video-information)" in toc
        assert "- [Summary](#summary)" in toc
        assert "- [Important Timestamps](#important-timestamps)" not in toc
        assert "## Chapter Summaries" not in toc

    @pytest.mark.unit
    def test_generate_markdown_single_chapter(self):
        """Test markdown generation for single chapter video."""
        summary_data = {
            "video_title": "Test Video",
            "video_url": "https://youtube.com/watch?v=test",
            "duration": 120,
            "language": "en",
            "uploader": "Test Channel",
            "chapters": [
                {
                    "title": "Full Video",
                    "start": 0,
                    "end": 120,
                    "summary": "This is a test summary with a key moment [1:30] and another [2:45].",
                    "timestamps": [
                        {"time": 90, "formatted": "1:30", "description": "Key moment 1"},
                        {"time": 165, "formatted": "2:45", "description": "Key moment 2"}
                    ],
                    "text": "Full video content"
                }
            ]
        }
        
        markdown = generate_markdown(summary_data)
        
        assert "# Test Video" in markdown
        assert "**Duration:** 2:00" in markdown
        assert "**Language:** English" in markdown
        assert "## Table of Contents" in markdown
        assert "- [Video Information](#video-information)" in markdown
        assert "- [Summary](#summary)" in markdown
        assert "- [Important Timestamps](#important-timestamps)" in markdown
        assert "## Video Information" in markdown
        assert "**Channel:** Test Channel" in markdown
        assert "**Original URL:** [https://youtube.com/watch?v=test](https://youtube.com/watch?v=test)" in markdown
        assert "## Summary" in markdown
        assert "This is a test summary with a key moment [1:30](https://youtube.com/watch?v=test&t=90s)" in markdown
        assert "## Important Timestamps" in markdown

    @pytest.mark.unit
    def test_generate_markdown_multiple_chapters(self):
        """Test markdown generation for multi-chapter video."""
        summary_data = {
            "video_title": "Test Video",
            "video_url": "https://youtube.com/watch?v=test",
            "duration": 300,
            "language": "en",
            "uploader": "Test Channel",
            "chapters": [
                {
                    "title": "Chapter 1",
                    "start": 0,
                    "end": 150,
                    "summary": "First chapter with important point [0:45].",
                    "timestamps": [
                        {"time": 45, "formatted": "0:45", "description": "Important point"}
                    ],
                    "text": "Chapter 1 content"
                },
                {
                    "title": "Chapter 2", 
                    "start": 150,
                    "end": 300,
                    "summary": "Second chapter with another point [3:15].",
                    "timestamps": [
                        {"time": 195, "formatted": "3:15", "description": "Another point"}
                    ],
                    "text": "Chapter 2 content"
                }
            ]
        }
        
        markdown = generate_markdown(summary_data)
        
        assert "# Test Video" in markdown
        assert "## Table of Contents" in markdown
        assert "- [Video Information](#video-information)" in markdown
        assert "- [Summary](#summary)" in markdown
        assert "- [Chapter Summaries](#chapter-summaries)" in markdown
        assert "  - [Chapter 1](#chapter-1)" in markdown
        assert "  - [Chapter 2](#chapter-2)" in markdown
        assert "## Video Information" in markdown
        assert "**Channel:** Test Channel" in markdown
        assert "**Original URL:** [https://youtube.com/watch?v=test](https://youtube.com/watch?v=test)" in markdown
        assert "## Chapter Summaries" in markdown
        assert "### Chapter 1" in markdown
        assert "### Chapter 2" in markdown
        assert "First chapter with important point [0:45](https://youtube.com/watch?v=test&t=45s)" in markdown
        assert "Second chapter with another point [3:15](https://youtube.com/watch?v=test&t=195s)" in markdown

    @pytest.mark.unit
    def test_save_markdown(self):
        """Test markdown file saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.md")
            test_content = "# Test\n\nThis is test content."
            
            save_markdown(test_content, test_file)
            
            assert os.path.exists(test_file)
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert content == test_content 