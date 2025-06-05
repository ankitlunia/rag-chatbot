from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from llama_cpp import Llama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.indexer import refresh_index
from utils.fetch_model import download_model_from_gdrive

from config import MODEL_PATH, EMBEDDING_MODEL, FAISS_INDEX_DIR, MAX_CONTEXT_CHARS, FIXED_RESPONSE

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware to allow all origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper Functions

def initialize_llm_and_embeddings():
    """Initialize the LLM model and embeddings."""
    llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=4)
    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return llm, embedding

def load_vectorstore():
    """Load the FAISS vector store from the specified directory."""
    return FAISS.load_local(FAISS_INDEX_DIR, embedding, allow_dangerous_deserialization=True)

def build_prompt(query: str, context: str) -> str:
    """Construct the prompt for the LLM based on the query and context."""
    return f"""
    You are a strict QA assistant. Only answer questions based on the context provided below. Do not go beyond the context.

    Context:
    {context}

    Question: {query}
    Answer:
    """

# Initialize model and embeddings
download_model_from_gdrive()
llm, embedding = initialize_llm_and_embeddings()

# Load FAISS vector store and create retriever
vectorstore = load_vectorstore()
retriever = vectorstore.as_retriever()

# Mount static files (for serving index.html and other static assets)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routes

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the homepage (index.html)."""
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/ask")
async def ask_question(request: Request):
    """Route for answering user questions."""
    data = await request.json()
    question = data.get("question", "").strip()

    if not question:
        return {"answer": "Please provide a valid question."}

    # Retrieve relevant documents
    documents = retriever.get_relevant_documents(question)

    if not documents:
        return {"answer": FIXED_RESPONSE}

    # Build context from retrieved documents (truncate to MAX_CONTEXT_CHARS)
    context = "\n".join(doc.page_content for doc in documents)[:MAX_CONTEXT_CHARS]

    # Construct prompt and generate response from LLM
    prompt = build_prompt(question, context)
    response = llm(prompt, max_tokens=2000, stop=["Question:"])

    answer = response.get("choices", [{}])[0].get("text", "").strip()
    return {"answer": answer if answer else FIXED_RESPONSE}

@app.post("/refresh-index")
def refresh_index_endpoint():
    """Route for refreshing the FAISS index."""
    refresh_index()
    global vectorstore, retriever
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever()
    return {"message": "Index refreshed from PDFs and URLs"}
