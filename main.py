from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from llama_cpp import Llama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from indexer import refresh_index

# Constants
MODEL_PATH = "./model/tinyllama.gguf"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FAISS_INDEX_DIR = "faiss_index"
MAX_CONTEXT_CHARS = 1200
FIXED_RESPONSE = "I don'tz"

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM and embeddings
llm = Llama(model_path=MODEL_PATH, n_ctx=512, n_threads=4)
embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

# Load vector store and retriever
def load_vectorstore():
    return FAISS.load_local(FAISS_INDEX_DIR, embedding, allow_dangerous_deserialization=True)

db = load_vectorstore()
retriever = db.as_retriever()

# Serve static files (index.html, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the homepage
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", "r") as f:
        return f.read()

# Route: Ask a question
@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    query = data.get("question", "").strip()

    if not query:
        return {"answer": "Please provide a valid question."}

    docs = retriever.get_relevant_documents(query)
    print("Retrieved Documents:", docs, "\n\n")

    if not docs:
        return {"answer": FIXED_RESPONSE}

    # Build context from documents
    context = "\n".join(doc.page_content for doc in docs)[:MAX_CONTEXT_CHARS]

    # Construct prompt
    prompt = f"""
You are a strict QA assistant. Only answer questions based on the context provided below. Do not go beyond the context.

Context:
{context}

Question: {query}
Answer:
    """

    # Generate response from LLM
    output = llm(prompt, max_tokens=2000, stop=["Question:"])
    result = output.get("choices", [{}])[0].get("text", "").strip()

    return {"answer": result if result else FIXED_RESPONSE}

# Route: Refresh FAISS index
@app.post("/refresh-index")
def refresh_index_endpoint():
    refresh_index()
    global db, retriever
    db = load_vectorstore()
    retriever = db.as_retriever()
    return {"message": "Index refreshed from PDFs and URLs"}
