#load regulation file and divide its content into smaller pieces
import json
from langchain_text_splitters import CharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document

with open("data/test/3314.json", 'r', encoding='utf-8') as file:
    data = json.load(file)

text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separator=" "
)


chunks = text_splitter.split_text(data["content"])


for index, chunk in enumerate(chunks):

    chunk_doc = Document (
        page_content= chunk,
        metadata= {"source_url": data['source_url'], "section": data['section'],"title": data['title'], "subchapter": data['subchapter'], "group": data['group'], "article": data['article'], "chunk_index": index}
    )
    chunks[index] = chunk_doc


print(chunks[0])
print("\n\n\n")
print(chunks[1])