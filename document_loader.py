import os
from PyPDF2 import PdfReader
from docx import Document
import wikipediaapi


def loadTextFile(file_path):
  with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read()
    return {
        'title': os.path.basename(file_path),
        'content': text,
    }
  
# def loadPDFFile(file_path):
#   reader = PdfReader(file_path)
#   text = ''

#   for page in reader.pages:
#     text += page.extract_text() + '\n'
#   return {
#     'title': os.path.basename(file_path),
#     'content': text,
#   } 

def loadPDFFile(file_path):
  out = []
  reader = PdfReader(file_path)
  for pageno, page in enumerate(reader.pages):
    txt = page.extract_text() or ""
    out.append({
        'title': f"{os.path.basename(file_path)}_page_{pageno+1}",
        'content': txt.strip(),
    })

  return out

def loadDocx(file_path):
  doc = Document(file_path)
  text = "\n".join(p.text for p in doc.paragraphs)

  return {
      'title': os.path.basename(file_path),
      'content': text,
  }


def loadDocuments(path = None , topics = None):
  documents = []

  if path:
    for f in os.listdir(path):
      fp = os.path.join(path, f)
      if f.endswith('.txt'):
        documents.append(loadTextFile(fp))
      if f.endswith('.pdf'):
        documents.extend(loadPDFFile(fp))
      if f.endswith('.docx'):
        documents.append(loadDocx(fp))

  if topics:
    wiki = wikipediaapi.Wikipedia(user_agent='RagSystem', language='en')
    for topic in topics:
      page = wiki.page(topic)
      if page.exists():
        documents.append({
            'title': page.fullurl,
            'content': page.text[:4000],
        })

  return documents



def _chunk_text(text, chunk_size, chunk_overlap):

    chunks = []
    start = 0

    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if not (0 <= chunk_overlap < chunk_size):
        raise ValueError("chunk_overlap must satisfy 0 <= overlap < chunk_size")

    text = text.strip()
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks


def chunking(text, chunk_size=500, chunk_overlap=50):

    if not text:
        return []

    text = text.strip()
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    results = []
    for para in paragraphs:
        if len(para) > chunk_size:
            sub_chunks = _chunk_text(para, chunk_size, chunk_overlap)
            results.extend(sub_chunks)
        else:
            results.append(para)

    return results
