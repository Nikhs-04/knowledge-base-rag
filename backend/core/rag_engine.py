"""
RAG (Retrieval-Augmented Generation) Engine with Ollama
"""
from typing import List, Dict, Optional
import ollama


class RAGEngine:
    """RAG implementation for question answering using Ollama"""
    
    def __init__(
        self,
        vector_store,
        model: str = "llama3.2",
        temperature: float = 0.3,
        max_tokens: int = 500
    ):
        """
        Initialize RAG engine with Ollama
        
        Args:
            vector_store: VectorStore instance
            model: Ollama model to use (llama3.2, llama3.1, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.vector_store = vector_store
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        print(f"✓ Using Ollama model: {model}")
    
    def query(
        self, 
        question: str,
        top_k: int = 5,
        include_sources: bool = True
    ) -> Dict[str, any]:
        """
        Answer a question using RAG
        
        Args:
            question: User's question
            top_k: Number of relevant chunks to retrieve
            include_sources: Whether to include source documents
            
        Returns:
            Dict with answer and metadata
        """
        # Step 1: Retrieve relevant documents
        print(f"Retrieving top {top_k} relevant chunks...")
        retrieved_docs = self.vector_store.search(
            query=question,
            top_k=top_k
        )
        
        if not retrieved_docs:
            return {
                'answer': "I couldn't find any relevant information in the knowledge base to answer your question.",
                'sources': [],
                'confidence': 'low',
                'retrieved_chunks': 0
            }
        
        # Step 2: Prepare context from retrieved documents
        context = self._prepare_context(retrieved_docs)
        
        # Step 3: Generate answer using Ollama
        print("Generating answer with Ollama...")
        answer = self._generate_answer(question, context)
        
        # Step 4: Prepare response
        response = {
            'answer': answer,
            'question': question,
            'retrieved_chunks': len(retrieved_docs)
        }
        
        if include_sources:
            response['sources'] = self._format_sources(retrieved_docs)
            response['confidence'] = self._calculate_confidence(retrieved_docs)
        
        return response
    
    def _prepare_context(self, retrieved_docs: List[Dict]) -> str:
        """
        Prepare context string from retrieved documents
        
        Args:
            retrieved_docs: List of retrieved document chunks
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            filename = doc['metadata'].get('filename', 'Unknown')
            text = doc['text']
            
            context_parts.append(
                f"[Document {i}: {filename}]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using Ollama
        
        Args:
            question: User's question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Create system prompt
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Instructions:
- Answer the question using ONLY the information from the provided documents
- If the answer cannot be found in the documents, say so clearly
- Be concise but comprehensive
- Cite specific documents when making claims
- If information is unclear or contradictory, mention it
- Use a professional and informative tone"""
        
        # Create user prompt
        user_prompt = f"""Context from documents:

{context}

Question: {question}

Please provide a clear and accurate answer based on the above context."""
        
        try:
            # Call Ollama API
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    }
                ],
                options={
                    'temperature': self.temperature,
                    'num_predict': self.max_tokens
                }
            )
            
            answer = response['message']['content'].strip()
            return answer
            
        except Exception as e:
            return f"Error generating answer with Ollama: {str(e)}"
    
    def _format_sources(self, retrieved_docs: List[Dict]) -> List[Dict]:
        """Format source information"""
        sources = []
        seen_files = set()
        
        for doc in retrieved_docs:
            filename = doc['metadata'].get('filename', 'Unknown')
            
            if filename not in seen_files:
                sources.append({
                    'filename': filename,
                    'file_type': doc['metadata'].get('file_type', 'Unknown'),
                    'relevance_score': round(doc.get('relevance_score', 0), 3)
                })
                seen_files.add(filename)
        
        return sources
    
    def _calculate_confidence(self, retrieved_docs: List[Dict]) -> str:
        """
        Calculate confidence level based on retrieval scores
        
        Args:
            retrieved_docs: Retrieved documents
            
        Returns:
            Confidence level: 'high', 'medium', or 'low'
        """
        if not retrieved_docs:
            return 'low'
        
        avg_score = sum(
            doc.get('relevance_score', 0) 
            for doc in retrieved_docs
        ) / len(retrieved_docs)
        
        if avg_score > 0.7:
            return 'high'
        elif avg_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def batch_query(
        self, 
        questions: List[str],
        top_k: int = 5
    ) -> List[Dict[str, any]]:
        """
        Process multiple questions in batch
        
        Args:
            questions: List of questions
            top_k: Number of chunks to retrieve per question
            
        Returns:
            List of answers
        """
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"\nProcessing question {i}/{len(questions)}")
            result = self.query(question, top_k=top_k)
            results.append(result)
        
        return results