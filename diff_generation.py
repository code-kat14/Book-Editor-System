from time import time
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
                    return text  # Return original

    # Split original into chunks

    # Process each chunk and combine results

    # Create diff between edited and original text

    # Create a DOCX with tracked changes