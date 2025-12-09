# LLM Client for Document Processing and Q&A
## Capstone Project: The Intelligent Q&amp;A chatbot/Tool 

This project provides a Python client for interacting with Large Language Models (LLMs), specifically the Gemini API, to perform various natural language processing tasks. It's designed to handle different document types, provide question-answering capabilities with caching, and extract key entities from text.

## Features

*   **Text Summarization:** Summarize plain text and content from various file types.
*   **Question Answering:** Answer questions based on provided context with built-in caching for improved performance.
*   **Entity Extraction:** Identify and extract key entities (like names, dates, locations) from text.
*   **Multi-format File Processing:** Supports reading and processing content from:
    *   PDF files (`.pdf`)
    *   CSV files (`.csv`)
    *   Excel files (`.xlsx`, `.xls`)
    *   JSON files (`.json`)
    *   HTML files (`.html`)
    *   Plain text files
*   **Web Content Summarization:** Summarize content directly from web URLs.
*   **Persistent Caching:** Caches LLM responses to avoid redundant API calls, saving time and resources.

## Setup

### 1. API Key Configuration

This project uses the Gemini API. You need to obtain an API key from Google AI Studio. Once you have your key, store it securely in Google Colab's Secrets Manager under the name `Googlechat_bot_api_key`.

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

genai.configure(api_key=os.getenv('Googlechat_bot_api_key'))
```

### 2. Install Dependencies

Install the necessary Python libraries:

```bash
pip install PyPDF2 pandas requests beautifulsoup4 google-generativeai httpx
```

### 3. Create `custom_exceptions.py`

Create a file named `custom_exceptions.py` in your project directory with the following content:

```python
# custom_exceptions.py

class LLMAPIError(Exception):
    """Custom exception for LLM API errors."""
    pass
```

### 4. `LLMClient` Class

Ensure your `LLMClient` class (from `smart_qa/client.py` or directly in your notebook) is defined as shown in the notebook cells, including the `CACHE_FILE_PATH` for persistent caching.

## Usage

### Initializing the Client

The `LLMClient` can be initialized with a `format` parameter if you intend to use its `extract_file` method directly. For other methods like `answer_questions_updated`, you can initialize without it.

```python
from smart_qa.client import LLMClient # Assuming client.py is in smart_qa directory, or adjust path

# For general LLM operations
llm_client = LLMClient(format=None) # Format is optional if not using extract_file directly

# For file-specific operations (e.g., extracting from a PDF)
pdf_client = LLMClient(format='pdf')
```

### Answering Questions

Use the `answer_questions_updated` method to get answers based on a context. This method utilizes caching.

```python
llm_client_instance = LLMClient(format=None) # Initialize once
llm_client_instance.answer_questions_updated('In Geography', 'How many Continents are there')
```

### Summarizing Documents

You can summarize text from various file types using the `summarize` method of the `LLMClient` or the standalone `summarize_pdf` function for PDFs.

**Using LLMClient.summarize (for various file types):**

```python
llm_client_instance = LLMClient(format='pdf')
summary_text = llm_client_instance.summarize('/content/drive/MyDrive/Caching APIs/Trial_files/ARIN-CALL-FOR-INTERNSHIP-APPLICATIONS-2026.pdf', 'pdf')
print(summary_text)
```

**Using the standalone `summarize_pdf` function (for PDFs):**

```python
# Make sure summarize_pdf function is defined in your environment
# @functools.lru_cache(maxsize=128)
def summarize_pdf(filepath: str) -> str:
    # ... (function body as in your notebook)

summarized_content = summarize_pdf('/content/drive/MyDrive/Caching APIs/Trial_files/ARIN-CALL-FOR-INTERNSHIP-APPLICATIONS-2026.pdf')
print(summarized_content)
```

### Extracting Entities

Extract key entities from a document using the `extract_entities` method.

```python
llm_client_instance = LLMClient(format='pdf')
entities = llm_client_instance.extract_entities('/content/drive/MyDrive/Caching APIs/Trial_files/ARIN-CALL-FOR-INTERNSHIP-APPLICATIONS-2026.pdf', 'pdf')
print(entities)
```


## Caching

The `LLMClient` implements a persistent caching mechanism for `answer_questions_updated`. Responses are stored in a JSON file at `smart-qa/cache.json`. If a question has been asked before, the cached answer will be returned, reducing API calls and latency. The `summarize` and `extract_entities` methods also use `functools.lru_cache` for in-memory caching during the current session.
