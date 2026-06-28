# 🚀 Medical HIS Development Setup Guide

**Status:** Planning  
**Last Updated:** June 28, 2026  
**Difficulty:** Intermediate (requires Docker, Python, Node.js knowledge)

---

## 📚 Tools & Technologies Used in This Project

### Overview
This project is a **FULL-STACK application** using multiple technologies across frontend, backend, ML/AI, and DevOps. Below is a complete breakdown of what tools you'll use and why.

### Frontend Stack
| Tool | Purpose | What It Does | Version |
|------|---------|-------------|---------|
| **Node.js** | JavaScript runtime | Run JavaScript outside browser, manage packages | 18+ |
| **npm** | Package manager | Download & manage JavaScript dependencies | 9+ |
| **React** | UI framework | Build interactive web components | 18+ |
| **Tailwind CSS** | Styling | Rapid UI development with utility classes | Latest |
| **Axios** | HTTP client | Make API calls to FastAPI backend | 1.6+ |
| **React Hook Form** | Form library | Validate medical form inputs | Latest |
| **React Router** | Routing | Navigate between pages (patient lookup, consultation, history) | 6+ |

### Backend Stack
| Tool | Purpose | What It Does | Version |
|------|---------|-------------|---------|
| **Python** | Language | Write all backend logic | 3.10+ |
| **FastAPI** | Web framework | Build REST API endpoints | 0.104+ |
| **Pydantic** | Data validation | Enforce FHIR schemas on API inputs | 2.5+ |
| **SQLAlchemy** | Database ORM | Query/manage patient data in SQLite | 2.0+ |
| **Uvicorn** | ASGI server | Run FastAPI application | 0.24+ |
| **Python-dotenv** | Config management | Load .env variables (API keys, secrets) | 1.0+ |
| **Requests** | HTTP client | Call HuggingFace API for LLM | 2.31+ |
| **Structlog** | Logging | Production-grade structured logging | Latest |
| **Pytest** | Testing | Unit & integration tests for backend | 7.4+ |

### Data & ML Stack
| Tool | Purpose | What It Does | Version |
|------|---------|-------------|---------|
| **SQLite 3** | Patient DB | Store patient records, medical history | Built-in |
| **Qdrant** | Vector DB | Store & search medical document embeddings | 1.7+ (Docker) |
| **HuggingFace API** | LLM Service | Call MedGemma-7B for medical Q&A (cloud) | Latest |
| **Sentence Transformers** | Embeddings | Create PubMed-BERT vectors for documents | 2.2+ |
| **rank-bm25** | Re-ranker | Two-stage retrieval (dense + lexical) | 0.2+ |
| **NumPy** | Math library | Vector operations, statistical analysis | 1.24+ |

### DevOps & Deployment
| Tool | Purpose | What It Does | Version |
|------|---------|-------------|---------|
| **Docker** | Containerization | Package app components in containers | 4.10+ |
| **Docker Compose** | Orchestration | Run multiple services (Qdrant, API, frontend) | 2.0+ |
| **Git** | Version control | Track code changes, push to GitHub | 2.40+ |
| **GitHub** | Repository hosting | Store code publicly (portfolio) | N/A |
| **GitHub Actions** | CI/CD | Auto-test, build, deploy (optional) | N/A |

### Healthcare Standards
| Tool | Purpose | What It Does |
|------|---------|-------------|
| **FHIR R4** | Data standard | Healthcare data interoperability format |
| **HL7 Concepts** | Terminology | Medical data validation |

---

## 🎯 Why Each Tool?

### Frontend (React Stack)
- **React:** Most popular frontend framework, large job market
- **Tailwind:** Fast responsive design without writing CSS
- **Axios:** Simple Promise-based HTTP client
- **React Hook Form:** Lightweight form validation (medical data)
- **React Router:** Standard SPA routing

### Backend (FastAPI Stack)
- **FastAPI:** Fastest Python web framework, great for APIs
- **Pydantic:** Automatic OpenAPI docs, FHIR schema validation
- **SQLAlchemy:** Industry-standard Python ORM
- **Uvicorn:** ASGI server (async support)
- **Structlog:** Structured logging for debugging production issues

### Data & ML
- **SQLite:** Simple, file-based DB (no server needed)
- **Qdrant:** Vector DB with built-in re-ranking support
- **HuggingFace API:** Access to latest LLMs without local install
- **Sentence Transformers:** Lightweight embeddings (PubMed-BERT)
- **rank-bm25:** Proven lexical re-ranker for information retrieval

### DevOps
- **Docker:** Industry standard containerization
- **Docker Compose:** Simplify local multi-service development
- **Git + GitHub:** Essential for portfolio projects

---

## 📥 What Gets Downloaded?

When you set up this project, here's what you'll download:

| Component | Size | Download Time | Where |
|-----------|------|---------------|-------|
| **Node.js + npm** | 200MB | 5 min | nodejs.org |
| **Python 3.11** | 100MB | 3 min | python.org |
| **Docker Desktop** | 500MB | 10 min | docker.com |
| **npm dependencies** (React, Axios, etc.) | 300MB | 5 min | npm registry |
| **Python dependencies** (FastAPI, etc.) | 200MB | 5 min | PyPI |
| **Docker images** (Qdrant, etc.) | 500MB | 10 min | Docker Hub |
| **HF token** (no download) | 0MB | 2 min | huggingface.co |
| **Your source code** | <10MB | <1 min | GitHub |
| **TOTAL** | ~1.8GB | ~45 min | Various |

**Important:** No LLM models downloaded locally! (MedGemma-7B accessed via HuggingFace API)

---

## 🛠️ Tools by Phase

### Phase 1: Foundation (Weeks 1-2)
- Node.js, npm → Setup frontend
- Python, FastAPI, Pydantic → Setup backend API
- Docker, Docker Compose → Start Qdrant
- Git → Version control

### Phase 2: RAG Integration (Weeks 3-4)
- Qdrant Client → Query vectors
- Requests → Call HF API for LLM
- Sentence Transformers → Create embeddings
- SQLAlchemy → Store patient data

### Phase 3: RAG Improvements (Weeks 5-6)
- rank-bm25 → Two-stage retrieval
- Pytest → Write tests
- Structlog → Production logging

### Phase 4: Testing & Docs (Week 7)
- Docker (multi-stage builds) → Optimize images
- GitHub → Push final code

### Phase 5: Article (Week 8)
- Markdown editor → Write Medium article
- GitHub → Link to code

---

## 💻 Recommended Tools for Development

### IDE/Editor
- **VS Code** (free, popular)
  - Extensions: Python, Pylance, Thunder Client (API testing)
- **PyCharm** (paid, enterprise)
  - Professional Python IDE with debugging

### API Testing
- **Thunder Client** (VS Code extension)
- **Postman** (free tier available)
- **Swagger UI** (auto-generated from FastAPI)

### Database Management
- **SQLite Browser** (free, view SQLite databases)
- **DBeaver** (free, professional DB tool)

### Version Control
- **Git** (command line)
- **GitHub Desktop** (GUI for Git)

---

---

## 📋 Prerequisites

### System Requirements
- **OS:** macOS 12+, Windows 11 (WSL2) or Ubuntu 20.04+
- **RAM:** 16GB minimum (32GB recommended for LLM)
- **Storage:** 50GB free (for models + vector DB)
- **GPU:** Optional but recommended (NVIDIA GPU with CUDA support)

### Software Requirements
- Python 3.10+
- Node.js 18+ (for frontend)
- Docker Desktop 4.10+
- Git
- VS Code or similar IDE

---

## 1️⃣ Install Prerequisites

### macOS
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install Node.js
brew install node

# Install Docker Desktop
brew install --cask docker

# Install Git
brew install git
```

### Windows (WSL2)
```bash
# Enable WSL2
wsl --install

# Install Python
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
```

### Ubuntu
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install nodejs npm
sudo apt install docker.io docker-compose
sudo apt install git
```

---

## 2️⃣ Clone & Setup Project

```bash
# Clone the repository (or create new one)
git clone https://github.com/YourUsername/medical-his-rag.git
cd medical-his-rag

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Return to root
cd ..
```

---

## 3️⃣ Install & Configure Ollama (LLM)

Ollama is a simple tool to run LLMs locally.

### Install Ollama
```bash
# macOS / Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download

# Verify installation
ollama --version
```

### Download Models
```bash
# Start Ollama daemon (runs in background)
ollama serve

# In a new terminal, pull models
ollama pull biomistr al:7b-4bit
ollama pull medgemma:7b-4bit
ollama pull meditron:70b-4bit  # Warning: 40GB, requires 40GB VRAM

# Verify models are installed
ollama list
```

**Output:**
```
NAME                  ID          SIZE      MODIFIED
biomistr al:7b-4bit   abc123...   4.0 GB    2 hours ago
medgemma:7b-4bit      def456...   5.0 GB    2 hours ago
```

### Test Ollama
```bash
# Query a model directly (for testing)
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "medgemma:7b-4bit",
    "prompt": "What is the treatment for hypertension?"
  }'
```

---

## 4️⃣ Setup Vector Database (Qdrant)

### Start Qdrant with Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant_vector_db
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      QDRANT_API_KEY: "your-secret-key-here"
    command: ./qdrant --api-key "your-secret-key-here"

  ollama:
    image: ollama/ollama:latest
    container_name: ollama_llm
    ports:
      - "11434:11434"
    volumes:
      - ./ollama_models:/root/.ollama
    environment:
      OLLAMA_HOST: "0.0.0.0:11434"
```

### Start Services
```bash
# Start Qdrant + Ollama
docker-compose up -d

# Verify containers are running
docker-compose ps

# View logs
docker-compose logs -f qdrant
docker-compose logs -f ollama

# Stop services
docker-compose down
```

### Test Qdrant
```bash
curl http://localhost:6333/health
# Should return: {"ok":true}
```

---

## 5️⃣ Setup Backend (FastAPI)

### Create `.env` file

Copy `.env.example` to `.env`:
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
```env
# Database
DATABASE_URL=sqlite:///./medical_his.db

# Vector DB
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your-secret-key-here
QDRANT_COLLECTION_NAME=medical_documents

# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=medgemma:7b-4bit
LLM_BASE_URL=http://localhost:11434

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=sk-medical-his-dev-12345

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_RERANKING=true
ENABLE_CITATIONS=true
```

### Create `backend/requirements.txt`

```
# Core Framework
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
sqlite==0.0.1

# Vector DB
qdrant-client==2.7.0

# LLM & Embeddings
ollama==0.1.1
transformers==4.35.0
torch==2.1.0
sentence-transformers==2.2.2

# Retrieval & Ranking
rank-bm25==0.2.2
numpy==1.24.0

# Logging & Monitoring
python-json-logger==2.0.7
structlog==24.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1

# Utilities
python-dotenv==1.0.0
aiofiles==23.2.1
```

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### Initialize Database
```bash
cd backend
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"
cd ..
```

### Start FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
cd ..
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Visit Swagger UI
open http://localhost:8000/docs
```

---

## 6️⃣ Setup Frontend (React)

### Create React App
```bash
cd frontend

# If starting from scratch
npx create-react-app .
# OR use Vite
npm create vite@latest . -- --template react

# Install dependencies
npm install

# Install additional libraries
npm install axios react-router-dom tailwindcss
npm install --save-dev tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Configure Tailwind
Edit `frontend/tailwind.config.js`:
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Create API Client
`frontend/src/services/api.js`:
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer sk-medical-his-dev-12345`
  }
});

export const patientAPI = {
  create: (data) => api.post('/patients', data),
  get: (id) => api.get(`/patients/${id}`),
  list: (params) => api.get('/patients', { params })
};

export const consultationAPI = {
  create: (data) => api.post('/consultations', data),
  get: (id) => api.get(`/consultations/detail/${id}`),
  getHistory: (patientId, params) => api.get(`/consultations/${patientId}`, { params })
};

export default api;
```

### Start Frontend
```bash
cd frontend
npm run dev
# OR
npm start

# Frontend will be at http://localhost:5173 (Vite) or 3000 (Create React App)
```

---

## 7️⃣ Local Development Workflow

### Terminal Setup (Recommended)

Open 4 terminals:

**Terminal 1: Docker services**
```bash
docker-compose up -d  # Start Qdrant
```

**Terminal 2: Ollama LLM**
```bash
ollama serve  # Ollama server
```

**Terminal 3: Backend API**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 4: Frontend**
```bash
cd frontend
npm run dev
```

### Verify Everything Works

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "healthy", ...}
   ```

2. **Frontend:**
   Open http://localhost:5173 in browser

3. **API Docs:**
   Open http://localhost:8000/docs for Swagger UI

---

## 8️⃣ Populate Medical Knowledge Base

### Create Medical Knowledge
```bash
# Download sample medical documents
cd backend/data
wget https://example.com/medical_documents.json

# Or create sample data
cat > medical_documents.json << 'EOF'
[
  {
    "id": "doc001",
    "title": "Meningitis Clinical Guidelines",
    "text": "Meningitis is inflammation of membranes surrounding brain...",
    "source_type": "clinical_guideline",
    "year": 2024
  }
]
EOF

cd ../..
```

### Index Documents
```bash
# Run indexing script (to be created)
cd backend
python scripts/index_medical_docs.py
cd ..
```

---

## 9️⃣ Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_api.py::test_health_check -v
cd ..
```

### Test API Endpoints
```bash
# Create patient
curl -X POST http://localhost:8000/patients \
  -H "Authorization: Bearer sk-medical-his-dev-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1980-06-15",
    "gender": "male"
  }'

# Create consultation
curl -X POST http://localhost:8000/consultations \
  -H "Authorization: Bearer sk-medical-his-dev-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-001",
    "chief_complaint": "Headache and fever"
  }'
```

---

## 🔟 Troubleshooting

### Ollama Connection Issues
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve

# Check model is available
ollama list
```

### Qdrant Connection Issues
```bash
# Check Qdrant health
curl http://localhost:6333/health

# View Qdrant logs
docker-compose logs qdrant

# Restart Qdrant
docker-compose restart qdrant
```

### Memory Issues
```bash
# If models are too large, use smaller versions:
# Edit .env to use:
# LLM_MODEL=biomistr al:7b-4bit (4GB)
# Instead of
# LLM_MODEL=meditron:70b-4bit (40GB)
```

### Port Already in Use
```bash
# If port 8000 is in use, change in .env:
API_PORT=8001

# Then start FastAPI on different port:
uvicorn app.main:app --port 8001
```

---

## 📚 Next Steps

1. ✅ Follow this guide to get local dev environment running
2. ✅ Verify all 4 services are working (Qdrant, Ollama, FastAPI, React)
3. ✅ Test health check endpoints
4. ✅ Create sample patients via API
5. ✅ Begin building features in Week 1-2

---

## 📞 Need Help?

- Check `/docs/ARCHITECTURE.md` for system design
- See `/docs/API_SPECIFICATION.md` for endpoint details
- Review `/PROJECT.md` for timeline and goals
