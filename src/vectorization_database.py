import chromadb
client = chromadb.PersistentClient(path="vector_data_base/")

from src.utils import download_hugging_face_embeddings

embeddings = download_hugging_face_embeddings()

def vectorization_text_chunks(text_chunks):
    collection = client.get_or_create_collection(name="my_rag_data")
    lenght = collection.count()
    vectors = []
    for i, chunk in enumerate(text_chunks):
        text = chunk.page_content
        values = embeddings.embed_query(text)
        metadata = chunk.metadata
        vectors.append({
            "id": str(f"vec{i+lenght}"),
            "values": values,
            "text": text,
            "metadata": metadata
        })
    return vectors

def vectorized_data_to_db(vectors):
    collection = client.get_or_create_collection(name="my_rag_data")
    vector_values = [vector["values"] for vector in vectors]
    vector_texts = [vector["text"] for vector in vectors]
    vector_ids = [vector["id"] for vector in vectors]
    vector_metadata = [vector["metadata"] for vector in vectors]
    
 
    collection.add(
      embeddings=vector_values,
      documents=vector_texts,
      metadatas=vector_metadata,
      ids=vector_ids
 )
    return collection