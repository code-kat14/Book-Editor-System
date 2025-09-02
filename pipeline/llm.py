from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

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
    prompt = f"<|system|>{SYS}</s><|user|>{text}</s><|assistant|>"
    ids = tok(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=800, do_sample=False, temperature=0.0)
    resp = tok.decode(out[0], skip_special_tokens=True)
    return resp.split("<|assistant|>")[-1].strip()
