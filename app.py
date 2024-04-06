from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

import gradio as gr

from dotenv import load_dotenv
import os


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


import chromadb
path = "vector_data_base/"
client = chromadb.PersistentClient(path=path)

from src.utils import download_hugging_face_embeddings, pdf_text_split,  url_text_split

from src.vectorization_database import vectorization_text_chunks, vectorized_data_to_db

from src.prompt import prompt_template

embeddings = download_hugging_face_embeddings()

def embedding_query(query):
    collection = client.get_collection(name="my_rag_data")
    result = collection.query(
        query_embeddings=embeddings.embed_query(query),
        n_results=2
    )
    context = result["documents"][0]
    return context


def pdf_extracter(input_file):
    print(input_file)
    text_chunks =  pdf_text_split(input_file)
    vectors = vectorization_text_chunks(text_chunks)
    vectorized_data_to_db(vectors)
    return "## Your Data is ready for RAG"

def url_extracter(url):
    text_chunks = url_text_split(url)
    vectors = vectorization_text_chunks(text_chunks)
    vectorized_data_to_db(vectors)
    return "## Your Data is ready for RAG"

def delete_vector_data(path):
    try:
        client = chromadb.PersistentClient("vector_data_base/")
        client.delete_collection(name="my_rag_data")
        return " ## Your Data is delete from VectorDB"
    except Exception as e:
        return str(e)    
    
history = []

def llm_response(message, history):
    question = str(message)
    context = embedding_query(question)
    inputs = {"context": context, "question": question}
    PROMPT=PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo-0125")
    llm_chain = LLMChain(prompt=PROMPT, llm=llm)
    result = llm_chain.invoke(inputs) 
    print(result)
    return str(result['text'])


file_upload = gr.File(label="Upload a file")
output_text_pdf = gr.Markdown(label="PDF response")
output_url = gr.Markdown(label="URL response")
chat_with_file = gr.ChatInterface(fn=llm_response)

upload_pdf = gr.Interface(
    fn=pdf_extracter,
    inputs=file_upload,
    outputs=output_text_pdf,
    title="PDF Extractor",
)

text_input = gr.Textbox(label="Enter URL")
url_extract = gr.Interface(
    fn=url_extracter,
    inputs=text_input,
    outputs=output_url,
    title="URL Extractor",
)

delete_vector_Database= gr.Interface(
    fn=delete_vector_data,
    inputs=gr.Button("detele"),
    outputs=gr.Markdown(),
    title="Delete vector DataBase"
)

demo = gr.TabbedInterface(
    [upload_pdf, url_extract, chat_with_file, delete_vector_Database],
    ["Upload PDF", "Extract URL", "Chat with File", "Delete Vector DataBase"]
)

# Launch the interface
if __name__ == "__main__":
    demo.launch()