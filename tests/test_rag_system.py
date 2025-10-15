"""
Test suite for RAG system
"""
import pytest
from backend.core.document_processor import DocumentProcessor
from backend.core.vector_store import VectorStore
from backend.core.rag_engine import RAGEngine


@pytest.fixture
def doc_processor():
    return DocumentProcessor(chunk_size=500, chunk_overlap=100)


@pytest.fixture
def vector_store():
    return VectorStore(
        persist_directory="./test_data/embeddings",
        collection_name="test_documents"
    )


def test_document_processing(doc_processor):
    """Test document processing"""
    # Create a test file
    test_file = "./test_data/sample.txt"
    with open(test_file, 'w') as f:
        f.write("This is a test document. " * 100)
    
    result = doc_processor.process_document(test_file)
    
    assert result['filename'] == 'sample.txt'
    assert len(result['chunks']) > 0
    assert 'text' in result['chunks'][0]


def test_vector_search(vector_store, doc_processor):
    """Test vector search functionality"""
    # Process and add documents
    test_file = "./test_data/sample.txt"
    doc = doc_processor.process_document(test_file)
    vector_store.add_documents([doc])
    
    # Search
    results = vector_store.search("test document", top_k=3)
    
    assert len(results) > 0
    assert 'text' in results[0]
    assert 'relevance_score' in results[0]


def test_rag_query(vector_store, rag_engine):
    """Test RAG query"""
    response = rag_engine.query(
        "What is this document about?",
        top_k=3
    )
    
    assert 'answer' in response
    assert 'sources' in response
    assert isinstance(response['answer'], str)