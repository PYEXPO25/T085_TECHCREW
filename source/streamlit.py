import os
import streamlit as st  
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings ,ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from PIL import Image
import re
import platform
import yt_dlp as youtube_dl # type: ignore
import io 
from reportlab.lib.pagesizes import letter # type: ignore
from reportlab.pdfgen import canvas # type: ignore
import instaloader # type: ignore
import glob
import requests

# Load environment variables from .env file
from dotenv import dotenv_values

config = dotenv_values(".env")  # Explicitly load from .env file
API_KEY = config.get("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Check your .env file!")

# Configure the API with the provided key
os.environ["GOOGLE_API_KEY"] = API_KEY  # Set the API Key explicitly for the session
genai.configure(api_key=API_KEY)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(api_key=API_KEY, model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")  # This creates the index

def load_vector_store(embeddings):
    try:
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        return new_db
    except FileNotFoundError:
        st.error("FAISS index not found. Please create it by processing PDF files first.")
        return None

def get_conversational_chain():
    prompt_template = """
    give day wise schedule 
    Answer the question in as detailed manner as possible from the provided context. Make sure to provide all the details. If the answer is not in the provided
    context, then just say, "answer is not available in the context." Don't provide the wrong answer.\n\n
    Context:\n {context}?\n
    Question:\n {question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(api_key=API_KEY, model="models/embedding-001")
    new_db = load_vector_store(embeddings)
    if new_db is None:  # If the index couldn't be loaded, exit early
        return

    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True
    )

    return response["output_text"]

# Streamlit app starts here
st.title("PDF Chatbot")
st.write("Upload your PDF file and ask questions about its content.")

pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

if pdf_file:
    pdf_filename = pdf_file.name  # Use the uploaded file's original name
    with open(pdf_filename, "wb") as f:
        f.write(pdf_file.getbuffer())

    if st.button("Process PDF"):
        try:
            raw_text = get_pdf_text([pdf_filename])
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("Done processing the PDF!")

        except Exception as e:
            st.error(f"Error processing the PDF file: {e}")

    user_question = st.text_input("Ask a Question about the PDF:")
    if user_question:
        answer = user_input(user_question)
        st.write("Reply:", answer)

