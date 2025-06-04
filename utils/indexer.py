import os
import glob
import requests
from bs4 import BeautifulSoup
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

PDF_FOLDER = "./pdfs"
URLS_FILE = "./urls.txt"
INDEX_FOLDER = "./faiss_index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def load_pdfs():
    docs = []
    for pdf in glob.glob(f"{PDF_FOLDER}/*.pdf"):
        loader = PyPDFLoader(pdf)
        pdf_docs = loader.load()
        # Clean up single newlines in the content
        for doc in pdf_docs:
            # Replace single newlines with spaces, but preserve double newlines
            doc.page_content = doc.page_content.replace('\n', ' ').replace('  ', ' ')
        docs.extend(pdf_docs)
    return docs

def extract_qa_from_accordion(soup):
    qa_pairs = []
    accordions = soup.find_all(class_="list-content")
    
    for accordion in accordions:
        # Find all question-answer pairs within the accordion
        questions = accordion.find_all(class_="tab-label")  # Adjust class name if different
        for q in questions:
            question = q.get_text(strip=True)
            # Find the corresponding answer (usually in a sibling or child element)
            answer = q.find_next(class_="tab-content")  # Adjust class name if different
            if answer:
                answer_text = answer.get_text(strip=True)
                qa_pairs.append(f"Q: {question}\nA: {answer_text}")
    
    return "\n\n".join(qa_pairs)

def scrape_urls():
    if not os.path.exists(URLS_FILE):
        return []

    docs = []
    with open(URLS_FILE, "r") as f:
        urls = f.read().splitlines()

    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.content, "html.parser")
            
            # Extract Q&A content from accordions
            qa_content = extract_qa_from_accordion(soup)
            
            if qa_content:
                docs.append(Document(page_content=qa_content, metadata={"source": url}))
            else:
                print(f"No Q&A content found in accordions for {url}")
                
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    return docs

def refresh_index():
    pdf_docs = load_pdfs()
    web_docs = scrape_urls()
    all_docs = pdf_docs + web_docs

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(all_docs)

    embedding = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = FAISS.from_documents(chunks, embedding)

    db.save_local(INDEX_FOLDER)
    print(f"FAISS index refreshed with {len(chunks)} chunks.")
