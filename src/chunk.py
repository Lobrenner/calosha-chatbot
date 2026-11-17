#load regulation file and divide its content into smaller pieces
import json
from langchain_text_splitters import CharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document


#make chunks of ~1000 characters to the nearest space character, each chnk has 200 characters of overlap

text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separator=" "
)

folder = Path("data/test")

reg_chunks = []

for item in folder.iterdir():
    with open(item, 'r', encoding='utf-8') as file:
        data = json.load(file)
   
    #make list of chunks
    chunks = text_splitter.split_text(data["content"])

    # iterate through list of chunks and add metadata to each one
    for index, chunk in enumerate(chunks):

        chunk_doc = Document (
            page_content= chunk,
            metadata= {"source_url": data['source_url'], "section": data['section'],"title": data['title'], "subchapter": data['subchapter'], "group": data['group'], "article": data['article'], "chunk_index": index, "identity": data['section'] + "_" + str(index)}
        )
        chunks[index] = chunk_doc
    reg_chunks.extend(chunks)

print(reg_chunks)