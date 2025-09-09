import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')


# Chunking needs to be done on a sentence basis
def chunk_blocks(blocks, min_chunk_size=1, max_chunk_size=500):
    chunks = []
    current_chunk = []
    current_size = 0

    for block in blocks:
        sentences = sent_tokenize(block.text)
        for sentence in sentences:
            sentence_size = len(sentence.split())
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(Chunk(text=' '.join(current_chunk)))
                current_chunk = []
                current_size = 0
            current_chunk.append(sentence)
            current_size += sentence_size

    if current_chunk:
        chunks.append(Chunk(text=' '.join(current_chunk)))

    return chunks