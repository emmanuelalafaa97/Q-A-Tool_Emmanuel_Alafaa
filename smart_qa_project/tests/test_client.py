from smart_qa.client import LLMClient
import pytest,pytest_mock
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def llm_client():
    return LLMClient(format='text')  # Adjust format as needed


def test_summarize_with_caching(llm_client, mocker):
    # Ensure a clean cache for this test
    LLMClient.summarize.cache_clear()

    test_text = "This is a test text for summarization."
    file_type = "text"

    # Create a fake response object with a .text attribute (same shape your code expects)
    mock_response = MagicMock()
    mock_response.text = "This is a summary."

    # Patch the underlying model call used inside summarize(), not summarize() itself
    mock_gen = mocker.patch.object(LLMClient.model, "generate_content", return_value=mock_response)

    # First call should invoke the model
    summary1 = llm_client.summarize(test_text, file_type)
    assert summary1 == mock_response.text
    mock_gen.assert_called_once()

    # Second call with the same args should hit the lru_cache and NOT call the model again
    summary2 = llm_client.summarize(test_text, file_type)
    assert summary2 == mock_response.text
    mock_gen.assert_called_once()



def test_answer_questions_updated_with_persistent_cache(llm_client, mocker, tmp_path):    
    # Setup a temporary cache file
    # create temp cache file
    temp_cache = tmp_path / "cache.json"
    sample_cache = {}
    temp_cache.write_text(json.dumps(sample_cache), encoding='utf-8')

    # Directly load into the class cache (this mirrors what module init would do)
    with open(temp_cache, 'r', encoding='utf-8') as f:
        LLMClient.cache = json.load(f)

    temp_cache_path = str(temp_cache)
    # Patch the CACHE_FILE_PATH to point to our temp file
    mocker.patch('smart_qa.client.CACHE_FILE_PATH', temp_cache_path)

    context = "This is some context."
    question = "What is the context about?"
    cache_items = f"{context}:{question}"
    cache_value = f"{question}"
    
    # Create a fake response object with a .text attribute (same shape your code expects)
    mock_response = MagicMock()
    mock_response.text = "The context is about something."
    
    # Patch the underlying model call used inside answer_questions_updated()
    mock_gen = mocker.patch.object(LLMClient.model, "generate_content", return_value=mock_response)

    # First call should invoke the model and store in cache
    answer1 = llm_client.answer_questions_updated(context, question)
    assert answer1 == mock_response.text
    mock_gen.assert_called_once()

    # Load the cache from the file to verify it was written
    with open(temp_cache_path, 'r') as f:
        cache_data = json.load(f)
    # ASSERT: cache_data should be a dict containing our key -> response.text
    assert isinstance(cache_data, dict)
    assert cache_value in cache_data
    assert cache_data[cache_value] == mock_response.text

    # Clear the mock call history
    mock_gen.reset_mock()

    # Second call should hit the persistent cache and NOT call the model again
    answer2 = llm_client.answer_questions_updated(context, question)
    assert answer2 == mock_response.text
    mock_gen.assert_not_called()

    # Clean up temporary cache file
    os.remove(temp_cache_path)
    cache = LLMClient.cache  # Access the class-level cache
    cache.clear()  # Clear the cache after test to avoid side effects
    if os.path.exists(temp_cache_path):
        os.remove(temp_cache_path)


def test_summarize_error_handling(llm_client, mocker):
    test_text = "This is a test text for summarization."
    file_type = "text"

    # Patch the underlying model call to raise an exception
    mocker.patch.object(LLMClient.model, "generate_content", side_effect=Exception("LLM API error"))

    with pytest.raises(Exception) as excinfo:
        llm_client.summarize(test_text, file_type)
    assert "LLM API error" in str(excinfo.value)

def test_answer_question_error_handling(llm_client, mocker):
    context = "This is some context."
    question = "What is the context about?"

    # Patch the underlying model call to raise an exception
    mocker.patch.object(LLMClient.model, "generate_content", side_effect=Exception("LLM API error"))

    with pytest.raises(Exception) as excinfo:
        llm_client.answer_question(context, question)
    assert "LLM API error" in str(excinfo.value)


def test_extract_file(llm_client, mocker):
    #create a temporary path for the file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
        tf.write("This is sample text for the temp file.")
        temp_path = tf.name
    # temp_path is a string path to the file
    print("Temp file created at:", temp_path)

    # later: read it (ensure the file was closed)
    content = Path(temp_path).read_text(encoding='utf-8')
    print(content)

    # Assuming extract_file just returns the text for 'text' file_type
    extracted_text = llm_client.extract_file(temp_path)    #this should be the file path
    assert extracted_text == content      #this should match the file content

    # cleanup when done
    os.remove(temp_path)



def test_init_sets_format():
    format_type = 'pdf'
    client = LLMClient(format=format_type)
    assert client.format == format_type

def test_cache_initialization(mocker, tmp_path):
    # create temp cache file
    temp_cache = tmp_path / "cache.json"
    sample_cache = {"sample_key": "sample_value"}
    temp_cache.write_text(json.dumps(sample_cache), encoding='utf-8')

    # Directly load into the class cache (this mirrors what module init would do)
    with open(temp_cache, 'r', encoding='utf-8') as f:
        LLMClient.cache = json.load(f)

    assert LLMClient.cache.get("sample_key") == "sample_value"

    # Clean up temporary cache file
    os.remove(temp_cache)

def test_extract_file_with_different_types(llm_client):
    # Test with text file type
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tf:
        tf.write("This is sample text for the temp file.")
        temp_path = tf.name
    # temp_path is a string path to the file
    print("Temp file created at:", temp_path)

    # later: read it (ensure the file was closed)
    content = Path(temp_path).read_text(encoding='utf-8')
    print(content)
    assert llm_client.extract_file(temp_path) == content

    # Test with unsupported file type (assuming it raises an error)
    #text_input = "Some input text"
    #llm_client.format = 'unsupported_type'
    #with pytest.raises(Exception):
        #llm_client.extract_file(text_input)
    # Clean up temporary cache file
    os.remove(temp_path)

def test_extract_entities(llm_client, mocker):
    test_text = "Barack Obama was the 44th president of the United States."

    # Create a fake response object with a .text attribute (same shape your code expects)
    mock_response = MagicMock()
    mock_response.text = "Entities: Barack Obama, United States"

    # Patch the underlying model call used inside extract_entities()
    mocker.patch.object(LLMClient.model, "generate_content", return_value=mock_response)
    
    entities = llm_client.extract_entities(test_text, 'text')   # remember your real method required you to pass file_type
    assert entities == mock_response.text

