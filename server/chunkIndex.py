import os
import json
from dotenv import load_dotenv
import tiktoken
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize OpenRouter client for embeddings
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY'),
)

# Initialize the tiktoken encoding for OpenAI's models
encoding = tiktoken.get_encoding("cl100k_base")  # Use the correct encoding for your model

# Function to read and split the content of a Markdown file into chunks of 800 tokens
def split_markdown_file_by_tokens(file_path: str, max_tokens: int = 800) -> list:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # Encode the entire text into tokens
    tokens = encoding.encode(data)
    
    # Split tokens into chunks of max_tokens
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        token_chunk = tokens[i:i + max_tokens]
        # Decode tokens back to text for API input
        chunks.append(encoding.decode(token_chunk))
    
    return chunks

# Function to create embeddings using OpenRouter's API
def create_embeddings(text: str, api_key: str = None, model: str = 'mistralai/codestral-embed-2505') -> list:
    embedding = openrouter_client.embeddings.create(
        model=model,
        input=text,
        encoding_format="float"
    )
    return embedding.data[0].embedding

# Function to process all Markdown files in a folder and save embeddings to a JSON file
def process_markdown_files(folder_path: str, api_key: str, output_file: str):
    embeddings_data = []
    total_files = len([name for name in os.listdir(folder_path) if name.endswith('.md')])
    processed_files = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            chunks = split_markdown_file_by_tokens(file_path)

            for i, chunk_text in enumerate(chunks):
                embeddings = create_embeddings(chunk_text)
                embeddings_data.append({
                    'file': filename,
                    'chunk_index': i,
                    'embedding': embeddings
                })
                print(f"Processed chunk {i+1}/{len(chunks)} of file {filename}")

            # Save embeddings to JSON file after processing each Markdown file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings_data, f, ensure_ascii=False, indent=4)
            
            processed_files += 1
            print(f"Processed file {processed_files}/{total_files}: {filename}")

def main():
    # Folder path and environment variables
    folder_path = '/home/pranay/Documents/ethglobal_singapore/LLMexperiments_ethglobal/ai-agent-template-openai/cyfrin-audit-reports/reports_md'
    api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('OPENAI_API_KEY')
    output_file = 'embeddings.json'

    if not api_key:
        print('OpenRouter API key (OPENROUTER_API_KEY) or OpenAI API key (OPENAI_API_KEY) is not set in the environment variables.')
        return

    try:
        # Process all Markdown files in the folder and save embeddings to a JSON file
        process_markdown_files(folder_path, api_key, output_file)
        print('Process completed successfully.')

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()