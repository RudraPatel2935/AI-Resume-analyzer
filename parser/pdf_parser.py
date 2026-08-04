import io

import pdfplumber


def extract_text_from_pdf(file_storage):
    file_storage.stream.seek(0)
    text_chunks = []
    with pdfplumber.open(file_storage.stream) as pdf:
        for page in pdf.pages:
            text_chunks.append(page.extract_text() or "")
    file_storage.stream.seek(0)
    return "\n".join(text_chunks)