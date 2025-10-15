"""
Vector store management using ChromaDB and embeddings
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """Manage document embeddings and similarity search"""
    
    def __init__(
        self, 
        persist_directory: str = "./data/embeddings",
        collection_name: str = "documents",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist embeddings
            collection_name: Name of the collection
            embedding_model: HuggingFace model for embeddings
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print("✓ Embedding model loaded")
    
    def add_documents(self, documents: List[Dict[str, any]]) -> Dict[str, int]:
        """
        Add documents to vector store
        
        Args:
            documents: List of processed documents
            
        Returns:
            Statistics about added documents
        """
        total_chunks = 0
        doc_ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            filename = doc['filename']
            
            for chunk in doc['chunks']:
                # Generate unique ID
                chunk_id = str(uuid.uuid4())
                doc_ids.append(chunk_id)
                
                # Store text
                texts.append(chunk['text'])
                
                # Store metadata
                metadatas.append({
                    'filename': filename,
                    'file_type': doc['file_type'],
                    'chunk_id': str(chunk['chunk_id']),
                    'start_pos': str(chunk['start_pos']),
                    'end_pos': str(chunk['end_pos'])
                })
                
                total_chunks += 1
        
        if not texts:
            return {'documents': 0, 'chunks': 0}
        
        # Generate embeddings
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
        
        # Add to collection
        self.collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✓ Added {total_chunks} chunks from {len(documents)} documents")
        
        return {
            'documents': len(documents),
            'chunks': total_chunks
        }
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            query,
            convert_to_numpy=True
        ).tolist()
        
        # Perform search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'relevance_score': 1 - results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def delete_collection(self):
        """Delete the entire collection"""
        self.client.delete_collection(name=self.collection_name)
        print(f"✓ Deleted collection: {self.collection_name}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get collection statistics"""
        count = self.collection.count()
        
        return {
            'collection_name': self.collection_name,
            'total_chunks': count,
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension()
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        # Get all IDs
        results = self.collection.get()
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"✓ Cleared {len(results['ids'])} chunks from collection")
        else:
            print("Collection is already empty")