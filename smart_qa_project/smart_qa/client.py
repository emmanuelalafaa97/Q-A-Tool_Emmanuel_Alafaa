# smart_qa/client.py
import os
import json
import logging
import functools
import google.generativeai as genai
from typing import Dict, Any
from .custom_exceptions import LLMAPIError, FileFormatError, ExtractionError
from dotenv import load_dotenv
#genai.configure(api_key=os.getenv("Germini_API_Key"))
import requests
from bs4 import BeautifulSoup # Import BeautifulSoup
import logging
from pathlib import Path
import pandas as pd
from PyPDF2 import PdfReader    #so that you can read pdfs
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_FILE_PATH = 'cache.json'

class LLMClient:
    load_dotenv()
    genai.configure(api_key=os.getenv("Germini_API_Key"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    cache = dict() # This is the class-level cache

    # Load cache from file if it exists when the class is defined
    try:
        if os.path.exists(CACHE_FILE_PATH):
            with open(CACHE_FILE_PATH, 'r') as f:
                cache = json.load(f)
                logger.info(f"Cache loaded from {CACHE_FILE_PATH}")
        else:
            logger.info(f"Cache file not found at {CACHE_FILE_PATH}, starting with empty cache.")
    except Exception as e:
        logger.error(f"Error loading cache from {CACHE_FILE_PATH}: {e}")
        cache = dict() # Ensure cache is empty on error


    def __init__(self, format: any) -> None:
        # TODO: Load API key and configure genai
        self.format = format
        #self.api_key = api_key
        #genai.configure(api_key=self.api_key)
        #self.format = str(format).lower()





    @functools.lru_cache(maxsize=128)
    def summarize(self, text: str, file_type:str) -> str:
        '''
        Summarizes the given text using the LLM.
        '''
        try :
          llm_client_instance = LLMClient(format=file_type)
          extracted_text = llm_client_instance.extract_file(text)
          # Use the input 'text' directly in the prompt
          prompt = f"Summarize the following document or text: {extracted_text}"
          response = LLMClient.model.generate_content(prompt)
          print(response.text)
          return response.text
        except Exception as e:
          print(f"Error loading {text}: {e}")
          print("Traceback:", traceback.format_exc())
          raise LLMAPIError(f"Failed to summarize content due to an LLM API error: {e}") # Raise custom exception error

    @functools.lru_cache(maxsize=128)
    def answer_question(self, context: str, question: str) -> str:
        '''
         Answers questions using the provided context.

        '''
        prompt = f"""Context: {context}
        Question: {question}
        Answer:"""
        response = LLMClient.model.generate_content(prompt)
        print(response.text)

    def answer_questions_updated(self, context: str, question: str) -> str:
        '''
         Answers questions using the provided context, utilizing a persistent cache.
        '''
        prompt = f"""Context: {context}
        Question: {question}
        Answer:"""

        if question not in LLMClient.cache: # Access class-level cache
            response_text = LLMClient.model.generate_content(prompt).text
            LLMClient.cache[question] = response_text # Update class-level cache
            # Save the updated cache to a JSON file
            try:
                # Ensure the directory exists before writing
                os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
                with open(CACHE_FILE_PATH, 'w') as f:
                    json.dump(LLMClient.cache, f)
                logger.info(f"Cache saved to {CACHE_FILE_PATH}")
            except Exception as e:
                logger.error(f"Error saving cache to {CACHE_FILE_PATH}: {e}")

            print(response_text)
            return response_text
        else:
            logger.info(f"Returning cached answer for question: {question}")
            cached_response = LLMClient.cache[question] # Access class-level cache
            print(cached_response) # Optionally print the cached response
            return cached_response

    def extract_file(self, file: any):
           """
              Extracts file and turns saves it to a json ouput
           """
           try:

              if self.format == 'csv':
                try:
                   df = pd.read_csv(file, encoding='utf-8-sig')
                   return df
                except Exception as e:
                      print(f"Error loading {file}: {e}")
                      print("Traceback:", traceback.format_exc())
              elif self.format == 'excel':
                try:
                   df = pd.read_excel(file)
                   return df
                except Exception as e:
                      print(f"Error loading {file}: {e}")
                      print("Traceback:", traceback.format_exc())
              elif self.format == 'json':
                try:
                   with open(file, 'r') as f:
                      df = json.load(f)
                      return df
                except Exception as e:
                      print(f"Error loading {file}: {e}")
                      print("Traceback:", traceback.format_exc())
              elif self.format == 'html':
                try:
                   with open(file, 'r') as f:
                      soup = BeautifulSoup(f, 'html.parser')
                      text = soup.get_text()
                      return text
                except Exception as e:
                      print(f"Error loading {file}: {e}")
                      print("Traceback:", traceback.format_exc())
              elif self.format == 'pdf':
                try:
                   with open(file, 'rb') as f:    #note rb here means read file =r and binary = b. pdf files should be read as binary files
                      pdf = PdfReader(f)
                      text = ''
                      for page in pdf.pages:
                         text += page.extract_text()
                      return text
                except Exception as e:
                   print(f"Error loading or saving {file}: {e}")
                   print("Traceback:", traceback.format_exc())
              else:
                 with open(file, 'r') as f:
                          text = f.read()
                          return text # Added return for consistency
           except Exception as e:
              print("Traceback:", traceback.format_exc())



    @functools.lru_cache(maxsize=128)
    def extract_entities(self, text: str, file_type: str) -> Dict[str, Any]:
        """
          Extracts key entities (People, Dates, Locations) from the text and returns them as a Python dictionary (JSON).
        """
        # TODO: Prompt for JSON output and parse it safely
        try :
          llm_client_instance = LLMClient(format=file_type)
          extracted_text = llm_client_instance.extract_file(text)
          # Use the input 'text' directly in the prompt
          prompt = f"Extract key names and figures from the following document or text: {extracted_text}"
          response = LLMClient.model.generate_content(prompt)
          print(response.text)
          return response.text
        except Exception as e:
          print(f"Error loading {text}: {e}")
          print("Traceback:", traceback.format_exc())


if __name__ == "__main__":
    llm_client = LLMClient(format='pdf')
    summary = llm_client.summarize(r'trial_documents\ARIN-CALL-FOR-INTERNSHIP-APPLICATIONS-2026.pdf', file_type='pdf')
    print("Summary:", summary)
