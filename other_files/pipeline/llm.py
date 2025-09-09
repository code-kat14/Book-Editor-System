from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

MODEL_ID = "microsoft/phi-3-mini-4k-instruct"  # swap for GPU: mistral-7b-instruct
device = "cuda" if torch.cuda.is_available() else "cpu"

tok = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16 if device=="cuda" else torch.float32,
    device_map="auto",
)

SYS = "You are a professional copy editor. Improve grammar, clarity, and consistency. Do not add facts. Do not reorder paragraphs."
def edit_chunk(text: str) -> str:
    # Capture leading and trailing whitespace (probably only need leading?)
    leading_whitespace = re.match(r'^\s*', text).group()
    trailing_whitespace = re.search(r'\s*$', text).group()
    
    # Strip whitespace for processing
    stripped_text = text.strip()
    
    # Skip processing if text is empty after stripping
    if not stripped_text:
        return text

    prompt = f"<|system|>{SYS}</s><|user|>{stripped_text}</s><|assistant|>"
    ids = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=800, do_sample=False, temperature=0.0)
    resp = tok.decode(out[0], skip_special_tokens=True)
    edited_text = resp.split("<|assistant|>")[-1].strip()
    
    # Reattach original whitespace
    return leading_whitespace + edited_text + trailing_whitespace
