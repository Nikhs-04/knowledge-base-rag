# 🔍 Knowledge Base RAG Search Engine

An intelligent document search system using Retrieval-Augmented Generation (RAG) with Ollama LLM and semantic search.

## 🌟 Features

- **Multi-format Support**: Upload PDF, DOCX, PPTX, and TXT files
- **Semantic Search**: Vector-based similarity search using sentence transformers
- **AI-Powered Answers**: Natural language responses using Ollama Llama 3.2
- **Source Attribution**: All answers cite their source documents
- **Confidence Scoring**: Reliability indicators for each answer
- **Modern UI**: Beautiful React frontend with real-time updates
- **RESTful API**: FastAPI backend with full documentation

## 🏗️ Architecture
```
Documents → Processing → Chunking → Embeddings → Vector DB (ChromaDB)
                                                        ↓
User Query → Embedding → Similarity Search → Top-K Retrieval
                                                        ↓
                                            Context + Query → Ollama LLM → Answer
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Ollama installed locally

### Backend Setup
```bash
# Clone repository
git clone [YOUR-REPO-URL]
cd knowledge-base-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend/api
python main.py
```

Backend runs at: `http://localhost:8000`

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Ollama Setup
```bash
# Install Ollama from https://ollama.com

# Pull model
ollama pull llama3.2

# Ollama runs automatically as a service
```

## 📚 API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

### Key Endpoints

- `POST /upload` - Upload documents
- `POST /query` - Search and get AI answers
- `GET /stats` - Get knowledge base statistics
- `DELETE /clear` - Clear all documents

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **Ollama** - Local LLM (Llama 3.2)
- **LangChain** - LLM orchestration
- **PyPDF, python-docx** - Document processing

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Lucide React** - Icons
- **CSS3** - Custom styling

## 📊 System Flow

1. **Document Upload**: Files are uploaded and processed
2. **Text Extraction**: Extract text from various formats
3. **Chunking**: Split into overlapping chunks (1000 tokens, 200 overlap)
4. **Embedding**: Generate vector embeddings for each chunk
5. **Storage**: Store in ChromaDB vector database
6. **Query Processing**: User query is embedded
7. **Retrieval**: Find top-K similar chunks using cosine similarity
8. **Generation**: Ollama generates answer from retrieved context
9. **Response**: Return answer with sources and confidence score

## 🎯 Key Features Explained

### Smart Chunking
- 1000 token chunks with 200 token overlap
- Preserves context across boundaries
- Maintains document metadata

### RAG Pipeline
- Retrieves relevant context before generation
- Reduces hallucinations
- Provides source attribution

### Confidence Scoring
- High (>70%): Strong relevance
- Medium (50-70%): Moderate relevance  
- Low (<50%): Weak relevance

## 📁 Project Structure
```
knowledge-base-rag/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   └── core/
│       ├── document_processor.py # Document handling
│       ├── vector_store.py       # ChromaDB operations
│       └── rag_engine.py         # RAG implementation
├── frontend/
│   └── src/
│       ├── App.jsx               # Main React component
│       └── App.css               # Styling
├── data/
│   ├── documents/                # Uploaded documents
│   └── embeddings/               # Vector database
└── requirements.txt              # Python dependencies
```

## 🧪 Testing

Upload sample documents and try these queries:
- "What is machine learning?"
- "Explain the main topics in these documents"
- "What are the key technologies mentioned?"

## 🚀 Deployment

### Backend (Railway/Render)
- Set environment variables
- Deploy from GitHub
- Update frontend API_URL

### Frontend (Vercel/Netlify)
- Connect GitHub repository
- Build command: `npm run build`
- Publish directory: `dist`

## 📝 Future Enhancements

- [ ] Multi-user support with authentication
- [ ] Document management (edit/delete)
- [ ] Query history
- [ ] Export answers to PDF
- [ ] Advanced filters
- [ ] Multiple LLM support
- [ ] Streaming responses

## 👨‍� Author

**Nikhita Moncy**
- GitHub: Nikhs-04
- LinkedIn: (https://www.linkedin.com/in/nikhita-moncy-bb904a210/)
- Email: nikhitamoncy2004@gmail.com

## 📄 License

MIT License

## 🙏 Acknowledgments

- Ollama for local LLM capabilities
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- FastAPI and React communities

---

⭐ **Star this repo if you find it helpful!**

Built for [Unthinkable Solutions] Internship Application
```

---
