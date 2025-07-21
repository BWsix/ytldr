# Test Suite Documentation

This directory contains comprehensive tests for the ytldr project.

## Test Structure

### Unit Tests (`test_summarizer.py`, `test_utils.py`)
- **Purpose**: Test individual functions and components in isolation
- **Coverage**: Core functionality, edge cases, error handling
- **Speed**: Fast execution (no external dependencies)
- **Markers**: `@pytest.mark.unit`

### Integration Tests (`test_integration.py`)
- **Purpose**: Test the complete pipeline end-to-end
- **Coverage**: Full workflow from download to markdown generation
- **Speed**: Slower (uses mocks for external services)
- **Markers**: `@pytest.mark.integration`, `@pytest.mark.slow`

## Running Tests

### Using the Test Runner
```bash
# Run all tests
python run_tests.py all

# Run only unit tests
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run fast tests (exclude slow ones)
python run_tests.py fast

# With coverage report
python run_tests.py unit --coverage

# With verbose output
python run_tests.py all --verbose
```

### Using pytest directly
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_summarizer.py

# Run tests with specific marker
pytest -m unit
pytest -m integration

# Run tests with coverage
pytest --cov=ytldr --cov-report=term-missing

# Run tests in parallel
pytest -n auto
```

## Test Categories

### Summarizer Tests
- **Ollama API calls**: Success and failure scenarios
- **Text extraction**: Time range filtering
- **Prompt generation**: Chapter and full video summaries
- **Timestamp parsing**: Valid and invalid formats
- **Video summarization**: With/without chapters, empty chapters

### Utils Tests
- **Title sanitization**: Directory name formatting
- **Duration formatting**: Time display
- **YouTube links**: Timestamp link generation
- **Markdown generation**: Chapter and full video formats
- **File operations**: Saving and directory creation

### Integration Tests
- **Complete pipeline**: Download → Transcribe → Summarize → Markdown
- **Chapter handling**: Videos with and without chapters
- **Language support**: Multi-language processing
- **Error handling**: Pipeline failures
- **Output validation**: File generation and content structure

## Mock Strategy

### External Dependencies
- **yt-dlp**: Mocked for video metadata extraction
- **Whisper**: Mocked for transcription results
- **Ollama**: Mocked for AI responses

### Test Data
- **Transcripts**: Realistic segment structures
- **Metadata**: Video info with chapters
- **AI Responses**: Structured summaries and timestamps

## Best Practices

1. **Isolation**: Each test is independent
2. **Realistic data**: Mock responses match real API formats
3. **Edge cases**: Test error conditions and boundary values
4. **Documentation**: Clear test names and docstrings
5. **Fast execution**: Unit tests run quickly for development

## Adding New Tests

1. **Unit tests**: Add to appropriate test file with `@pytest.mark.unit`
2. **Integration tests**: Add to `test_integration.py` with `@pytest.mark.integration`
3. **Slow tests**: Mark with `@pytest.mark.slow` for long-running tests
4. **Follow naming**: Use descriptive test method names
5. **Add docstrings**: Explain what each test validates

## Continuous Integration

The test suite is designed to run in CI environments:
- Fast execution for quick feedback
- Comprehensive coverage of functionality
- Clear pass/fail indicators
- Coverage reporting for code quality 