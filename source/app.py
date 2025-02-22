from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from datetime import datetime
from models import User, ChatMessage, Query
from database import db

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in .env file!")

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Use PostgreSQL/MySQL in production
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Bind db to app AFTER setting config
db.init_app(app)

# Import models AFTER db is initialized
from models import User, ChatMessage, Query

# Create database tables
with app.app_context():
    db.create_all()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# PDF processing functions
def get_pdf_text(pdf_path):
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(api_key=API_KEY, model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question in as detailed a manner as possible from the provided context.
    If the answer is not in the provided context, say "answer is not available in the context."
    
    Context:\n {context}?\n
    Question:\n {question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

import pickle

def load_faiss_index():
    """Load the FAISS index and corresponding embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(api_key=API_KEY, model="models/embedding-001")
    
    # Load FAISS index
    index_path = "faiss_index"
    try:
        new_db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        return new_db
    except Exception as e:
        print(f"Error loading FAISS index: {str(e)}")
        return None

def process_question(user_question):
    """Retrieve context from FAISS and ask Gemini for a response."""
    faiss_index = load_faiss_index()
    if not faiss_index:
        return "Error: FAISS index could not be loaded."

    # Perform similarity search
    docs = faiss_index.similarity_search(user_question, k=3)  # Get top 3 matches
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else "No relevant context found."

    # Send question with context to Gemini
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Context:\n{context}\n\nQuestion:\n{user_question}\n\nAnswer:"
    response = model.generate_content(prompt)

    return response.text if response else "Error generating response from Gemini."

def save_faiss_index(text_chunks):
    """Create and save FAISS index from text chunks."""
    embeddings = GoogleGenerativeAIEmbeddings(api_key=API_KEY, model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

    index_path = "faiss_index"
    vector_store.save_local(index_path)
    print("FAISS index saved successfully!")


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error during registration!', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    model = genai.GenerativeModel('gemini-pro')
    
    if request.method == 'POST':
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                try:
                    raw_text = get_pdf_text(filepath)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    
                    system_msg = ChatMessage(user_id=session['user_id'], content=f"✅ PDF '{filename}' processed!", type='assistant')
                    db.session.add(system_msg)
                    db.session.commit()
                    
                except Exception as e:
                    flash(f'Error processing PDF: {str(e)}', 'error')
        
        elif 'question' in request.form:
            question = request.form['question']
            
            user_msg = ChatMessage(user_id=session['user_id'], content=question, type='user')
            db.session.add(user_msg)
            
            try:
                response = model.generate_content(f"Provide a helpful answer: {question}")
                
                assistant_msg = ChatMessage(user_id=session['user_id'], content=response.text, type='assistant')
                db.session.add(assistant_msg)
                
            except Exception as e:
                assistant_msg = ChatMessage(user_id=session['user_id'], content=f"Error: {str(e)}", type='assistant')
                db.session.add(assistant_msg)
            
            db.session.commit()

    messages = ChatMessage.query.filter_by(user_id=session['user_id']).order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chatbot.html', messages=messages)

@app.route('/history')
@login_required
def history():
    user_queries = Query.query.filter_by(user_id=session['user_id']).order_by(Query.timestamp.desc()).all()
    return render_template('history.html', queries=user_queries)

if __name__ == '__main__':
    app.run(debug=True)
