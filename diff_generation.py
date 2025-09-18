import re
from time import time
from typing import List
from huggingface_hub import InferenceClient

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

SYSTEM_PROMPT = """You are an editor applying Chicago Manual of Style conventions to English prose.
Revise for: clarity; concision; consistent serial/Oxford comma; em dashes (—) without spaces; American punctuation with commas/periods inside closing quotation marks; logical paragraphing; headline-style capitalization for headings; numerals vs words in general prose (spell out zero through one hundred unless a clear exception applies); standardize ellipses with spaces (… or . . .) according to prose usage.
Do not invent sources or modify factual claims. Preserve meaning. If citations or footnotes exist, leave their structure intact.
Output only the revised text.
"""

class TrackChangesEditor:
    def __init__(self):
        self.client = InferenceClient(model=MODEL_ID)
        self.system_prompt = SYSTEM_PROMPT

    # Create prompt to send to the model
    def create_edit_prompt(self, text: str) -> str:
        """Create the prompt for the model"""
        return f"""<|system|>
        {self.system_prompt}</s>
        <|user|>
        Please edit the following text according to Chicago Manual of Style guidelines:

        {text}</s>
        <|assistant|>
        """
    # Call the model to get the edited text
    def edit_text(self, text: str, max_retries: int = 3) -> str:
        prompt = self.create_edit_prompt(text)
        
        for attempt in range(max_retries):
            try:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=2048,  # For larger text chunks, may need to change
                    temperature=0.1,
                    return_full_text=False # Return the new tokens generated after the prompt
                )
                return response.strip()
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"Failed to process text after {max_retries} attempts")
                    return text

    # Split original into chunks
    def split_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            para_size = len(paragraph)
            
            # If paragraph is too big, split it into sentences
            if para_size > max_chunk_size:
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
                
                sentences = re.findall(r'[^.!?]+[.!?]*', paragraph)
                sentence_chunks = []
                temp_chunk = []
                temp_size = 0
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    sent_size = len(sentence)
                    if temp_size + sent_size > max_chunk_size and temp_chunk:
                        sentence_chunks.append(' '.join(temp_chunk))
                        temp_chunk = [sentence]
                        temp_size = sent_size
                    else:
                        temp_chunk.append(sentence)
                        temp_size += sent_size + 1
                
                if temp_chunk:
                    sentence_chunks.append(' '.join(temp_chunk))
                
                chunks.extend(sentence_chunks)
                continue
            
            if current_size + para_size + 2 > max_chunk_size and current_chunk:  # +2 for \n\n
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(chunk_text)
                current_chunk = [paragraph]
                current_size = para_size
            else:
                current_chunk.append(paragraph)
                current_size += para_size + 2  # +2 for \n\n
    
        # Add the last chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(chunk_text)
        
        return chunks

    # Process each chunk and combine results

    # Create diff between edited and original text

    # Create a DOCX with tracked changes