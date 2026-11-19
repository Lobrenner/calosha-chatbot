#load regulation file and divide its content into smaller pieces
import json
from langchain_text_splitters import CharacterTextSplitter
from pathlib import Path
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

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
            metadata= {"source_url": data['source_url'], "section": data['section'],"title": data['title'], "subchapter": data['subchapter'], "group": data['group'], "article": data['article'], "chunk_index": index, "identity": item.stem + "_" + str(index)}
        )
        chunks[index] = chunk_doc
    reg_chunks.extend(chunks)


#use pre loaded model to generate embeddings, this model is lightweight
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#test embedding
#calculate embeddings
Test_chunks = [reg_chunks[0].page_content, reg_chunks[1].page_content, 
               reg_chunks[2].page_content, reg_chunks[3].page_content
               ]

test_question = "Can compressed air be used to clean clothing?"

embeddings1 = model.encode(test_question)
#print(embeddings1.shape)
embeddings = model.encode(Test_chunks)
#print(embeddings.shape)

#calculate embedding similarities
similarities = model.similarity(embeddings1, embeddings)
#print(similarities)


best_similarity = similarities[0].argmax()
#retrieve highest similarity values index from simliarity output (pyTorch Tensor) then convert to integer with .item
index = similarities[0].argmax().item()

metadata_for_best = reg_chunks[index].metadata
best_section = metadata_for_best['section']
chunk_index = metadata_for_best['chunk_index']

print(f"Question: {test_question} \n")
print(f"Best Matching Section: {best_section}")
print(f"similarity score: {similarities[0][best_similarity]}")
print(f"Chunk Index: {chunk_index}")