from pipeline.docx_io import read_docx_blocks, write_docx_from_blocks
from pipeline.preprocess import normalize
from pipeline.chunking import chunk_blocks
from pipeline.llm import edit_chunk
from pipeline.diff import word_diff
from pipeline.track_changes import apply_diffs_to_paragraph
from core.storage import put_obj, get_obj_url
from apps.api_fastapi.routers.jobs import JOB_STATUS

# Remove Celery imports and use Flask's job status handling
JOB_STATUS = {}

def process_docx(job_id: str, key_in: str):
    JOB_STATUS[job_id] = "Processing"

    try:
        # 1. Read docx blocks
        blocks = read_docx_blocks(key_in)
        normalized = normalize(blocks)

        # 2. Chunk & edit
        chunks = chunk_blocks(normalized)
        edited = [edit_chunk(c.text) for c in chunks]
        merged = "".join(edited)

        # 3. Apply diffs & track changes
        doc, para_map = read_docx_blocks(key_in, return_doc=True)
        for pid, updated_text in merged.paragraphs.items():
            diffs = word_diff(para_map[pid].text, updated_text)
            apply_diffs_to_paragraph(para_map[pid], diffs)

        # 4. Write output
        out_bytes = write_docx_from_blocks(doc)
        key_out = f"results/{job_id}.docx"
        put_obj(key_out, out_bytes)

        JOB_STATUS[job_id] = "Completed"
        return {"output_key": key_out, "download_url": get_obj_url(key_out)}
    
    except Exception as e:
        JOB_STATUS[job_id] = "Failed"
        raise e
