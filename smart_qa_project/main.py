# smart_qa/main.py
from smart_qa.client import LLMClient
import os

def user_interface():
    welcome_text = '''Welcome to the Smart QA System!\n Please choose an option: '''
    choice = input(welcome_text + '\n1. Summarize Document\n2. Answer Question\nYour choice: ')
    llm_client = LLMClient(format='pdf')  # You can modify the format as needed

    if choice == '1':
        file_path = input('Enter the path to the document: ')
        file_type = os.path.splitext(file_path)[1][1:]  # Extract file extension without dot
        summary = llm_client.summarize(file_path, file_type=file_type)
        print("Summary:", summary)

    elif choice == '2':
        context = input('Enter the context: ')
        question = input('Enter your question: ')
        answer = llm_client.answer_question(context, question)
        print("Answer:", answer)

    else:
        print("Invalid option. Please enter 1 or 2.")


if __name__ == "__main__":
    user_interface()