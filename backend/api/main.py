"""
FastAPI backend for Knowledge Base RAG system
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from core.document_processor import DocumentProcessor
from core.vector_store import VectorStore
from core.rag_engine import RAGEngine

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Base RAG API",
    description="Search across documents with AI-powered answers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
doc_processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
vector_store = VectorStore(
    persist_directory="./data/embeddings",
    collection_name="documents"
)
rag_engine = RAGEngine(
    vector_store=vector_store,
    model="llama3.2",
    temperature=0.3
)

# Data directory
UPLOAD_DIR = Path("./data/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic models
class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    include_sources: bool = True


class QueryResponse(BaseModel):
    answer: str
    question: str
    sources: Optional[List[dict]] = None
    retrieved_chunks: int
    confidence: Optional[str] = None


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    collection_name: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Knowledge Base RAG API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload",
            "query": "/query",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload and process documents
    
    Args:
        files: List of document files
        
    Returns:
        Processing status and statistics
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_files = []
    processed_docs = []
    
    try:
        # Save uploaded files
        for file in files:
            # Validate file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in doc_processor.SUPPORTED_FORMATS:
                continue
            
            # Save file
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(str(file_path))
        
        if not uploaded_files:
            raise HTTPException(
                status_code=400, 
                detail="No valid document files provided"
            )
        
        # Process documents
        for file_path in uploaded_files:
            try:
                doc = doc_processor.process_document(file_path)
                processed_docs.append(doc)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
        
        if not processed_docs:
            raise HTTPException(
                status_code=500,
                detail="Failed to process any documents"
            )
        
        # Add to vector store
        stats = vector_store.add_documents(processed_docs)
        
        return {
            "status": "success",
            "message": f"Processed {stats['documents']} documents",
            "statistics": stats,
            "files": [Path(f).name for f in uploaded_files]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    Query the knowledge base
    
    Args:
        request: Query parameters
        
    Returns:
        Answer with sources and metadata
    """
    try:
        result = rag_engine.query(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get knowledge base statistics"""
    try:
        stats = vector_store.get_stats()
        
        # Count documents
        uploaded_docs = list(UPLOAD_DIR.glob('*'))
        doc_count = len([
            d for d in uploaded_docs 
            if d.suffix.lower() in doc_processor.SUPPORTED_FORMATS
        ])
        
        return StatsResponse(
            total_documents=doc_count,
            total_chunks=stats['total_chunks'],
            collection_name=stats['collection_name']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        # Clear vector store
        vector_store.clear_collection()
        
        # Delete uploaded files
        for file_path in UPLOAD_DIR.glob('*'):
            if file_path.is_file():
                file_path.unlink()
        
        return {
            "status": "success",
            "message": "Knowledge base cleared"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "vector_store": "connected",
        "model": rag_engine.model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )