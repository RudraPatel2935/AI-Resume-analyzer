from docx import Document


def extract_text_from_docx(file_storage):
    file_storage.stream.seek(0)
    document = Document(file_storage.stream)
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    file_storage.stream.seek(0)
    return "\n".join(paragraphs)