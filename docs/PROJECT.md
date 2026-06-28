# 🏥 Medical RAG HIS Web Application — Portfolio Project

**Author:** Patapee Siribenjaponsakun  
**Project:** Medical HIS (Health Information System) with RAG  
**Status:** Planning Phase  
**Start Date:** June 28, 2026  
**Target Completion:** Mid-August 2026  

---

## 📋 Project Overview

### Primary Goal: Build a Production-Grade Medical HIS Web App
**"A healthcare information system with AI-powered medical Q&A, demonstrating backend engineering skills (FastAPI, LLM deployment, containerization, medical data standards)"**

Build a **functional medical HIS application** that:
- ✅ Accepts standardized medical inputs (patient data, complaints, vital signs)
- ✅ Returns AI-powered medical insights using RAG (citations + confidence)
- ✅ Follows healthcare standards (FHIR JSON responses)
- ✅ Runs locally with Docker containerization
- ✅ Shows production-ready backend patterns (error handling, logging, validation)
- ✅ Can be deployed and demoed to stakeholders

### Secondary Goal: Extract RAG Article
After HIS app is complete → Extract the RAG improvements as a Medium article:
**"Building a Healthcare RAG System: What I Learned Creating a Medical HIS"**

### Why This Approach Works
- 🎯 **Portfolio value**: Real working app > article (shows engineering + practical skills)
- 💼 **Demonstration**: Can demo to employers/clients, not just write about it
- 📚 **Content**: Article comes naturally from the implementation
- 🏥 **Healthcare focus**: Actual use case, not just benchmarking
- ⚡ **Skills showcase**: FastAPI, LLM ops, containerization, FHIR standards

---

## 🎯 Success Criteria (HIS App Development)

| Metric | Target |
|--------|--------|
| **Functionality** | All 3 features working end-to-end |
| **Code Quality** | Production-ready, well-documented, error handling |
| **Deployment** | Docker container runs locally without issues |
| **API Quality** | Swagger docs complete, FHIR-compliant responses |
| **Performance** | Response latency < 2 sec (with model inference) |
| **Implementation Time** | 6–8 weeks |
| **Portfolio Ready** | Can demo to employers/clients |
| **Article Quality** | 2000+ words extracted from implementation |

---

## 🏥 HIS Features (3 Core Modules)

### Feature #1: Medical Query Interface
**Input:**
```json
{
  "patient_id": "P12345",
  "patient_name": "John Doe",
  "age": 45,
  "chief_complaint": "Persistent headache and fever",
  "vital_signs": {
    "blood_pressure": "140/90",
    "heart_rate": 95,
    "temperature": 38.5,
    "respiratory_rate": 18
  },
  "additional_symptoms": ["nausea", "sensitivity to light"]
}
```

**Output (FHIR-compliant):**
```json
{
  "consultation_id": "C-20260628-001",
  "patient_reference": "Patient/P12345",
  "ai_assessment": {
    "primary_impression": "Possible viral meningitis or severe migraine",
    "confidence": 0.87,
    "reasoning": "Triad of fever, headache, and photophobia suggests..."
  },
  "evidence_based_recommendations": [
    {
      "recommendation": "Immediate medical evaluation recommended",
      "priority": "HIGH",
      "supporting_evidence": [...]
    }
  ],
  "sources": [
    {
      "title": "Meningitis Clinical Guidelines",
      "relevance_score": 0.94,
      "excerpt": "..."
    }
  ],
  "uncertainty_notes": ["Limited history on medication history"],
  "timestamp": "2026-06-28T14:30:00Z",
  "response_time_ms": 1240
}
```

### Feature #2: Patient History Management
- Store patient info (demographics, medical history)
- Track query history with responses
- Support for FHIR Patient resource format
- Simple patient lookup by ID/name

### Feature #3: Medical Knowledge Base
- Pre-indexed medical documents (PubMed abstracts, clinical guidelines)
- Vector DB (Qdrant) for semantic search
- RAG system to ground responses in evidence
- Citation tracking for all recommendations

---

## 🔧 Tech Stack Specification

### Backend
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API Framework** | FastAPI 0.104+ | REST API with async support |
| **Data Models** | Pydantic | Input validation (FHIR schemas) |
| **LLM Inference** | Ollama + HuggingFace | Model serving (BioMistral/Meditron/MedGemma) |
| **Vector DB** | Qdrant | Medical document embeddings |
| **Embeddings** | PubMed-BERT | Domain-specific text embeddings |
| **Logging** | Python logging + structlog | Production logging |
| **Error Handling** | Custom exceptions | Graceful error responses |

### Frontend (Simple)
| Component | Technology |
|-----------|-----------|
| **UI Framework** | React 18 or Vue 3 (TBD) |
| **API Client** | Axios/Fetch |
| **Form Handling** | React Hook Form or Vee Validate |
| **Styling** | Tailwind CSS |
| **State** | React Context or Pinia |

### Deployment
| Component | Technology |
|-----------|-----------|
| **Containerization** | Docker + Docker Compose |
| **Model Quantization** | 4-bit (bitsandbytes) |
| **Orchestration** | Docker Compose (dev), K8s ready |
| **Health Checks** | FastAPI lifespan events |

### Medical Standards
| Standard | Implementation |
|----------|----------------|
| **FHIR** | Response schemas (Patient, Observation, Condition) |
| **HL7 Concepts** | Medical terminology validation |
| **Data Privacy** | Structured logging (no PII in logs) |

---

## 📍 Tech Stack Summary

```
Frontend                Backend                        Infrastructure
└─ React/Vue          └─ FastAPI                      └─ Docker Compose
  └─ Tailwind           ├─ Pydantic (FHIR validation)    ├─ Qdrant (vector DB)
  └─ Axios              ├─ Ollama (model serving)        └─ Ollama (LLM inference)
                        │  ├─ BioMistral-7B
                        │  ├─ Meditron-70B
                        │  └─ MedGemma-7B
                        └─ PubMed-BERT (embeddings)
```

---

## 📂 Project Structure (New HIS Layout)

### Why This Repo?
| Aspect | fenil210 | iamaber | Winner |
|--------|----------|---------|--------|
| **LLM** | BioMistral-7B (local) | OpenAI/Gemini (API) | fenil210 ✅ |
| **Complexity** | ~500 LOC | ~2K LOC | fenil210 ✅ |
| **Retriever** | Qdrant + semantic chunking | FAISS + transformers | fenil210 ✅ |
| **Gaps to Fix** | Clear (no re-rank, no citations) | Harder to modify (API deps) | fenil210 ✅ |

**Link:** https://github.com/fenil210/Medical-RAG

---

## 🔧 3 Core Improvements (The Article's Spine)

### Improvement #1: LLM Upgrade
**Problem:** BioMistral-7B only achieves ~58% on MedQA  
**Solution:** Benchmark newer models (Meditron-70B, MedGemma-7B)  
**Tradeoff:** Higher accuracy (+14%) vs. higher latency (+200ms) and VRAM (+25GB)

**Experiment Plan:**
```
Test Set: MMLU-Med subset (30 questions)
Models to Benchmark:
  - BioMistral-7B (baseline)
  - Meditron-70B (guideline-focused)
  - MedGemma-7B (current SOTA)

Metrics:
  - Accuracy (%)
  - Latency (ms per response)
  - VRAM usage (4-bit quantization)
  - Cost (inference cost per query)
```

**Article Section Title:** *"The LLM Bottleneck: Why Retrieval Alone Isn't Enough"*

---

### Improvement #2: Add Re-ranking Layer
**Problem:** Single-stage retrieval (dense search only) leaves relevant documents unsorted  
**Solution:** Add neural re-ranker (ModernBERT + lightweight classifier pattern)  
**Tradeoff:** +0.5–1% accuracy, +50ms latency, +3GB VRAM

**Implementation Plan:**
```
Original Pipeline:
  Query → Dense Embedding → Top-K Retrieval → LLM

Improved Pipeline:
  Query → Dense Embedding → Top-K Retrieval 
        → Neural Re-ranker (re-sort top-K) 
        → LLM
```

**Benchmark Metric:**
- Precision@5: Fraction of top-5 results actually relevant
- Recall@10: Fraction of all relevant docs in top-10

**Article Section Title:** *"Beyond Semantic Search: Why Single-Stage Retrieval Fails"*

---

### Improvement #3: Add Explainability & Citations
**Problem:** LLM returns answer only; clinicians need to see evidence  
**Solution:** Track source documents + add confidence scoring  
**Tradeoff:** Minimal (metadata tracking only, ~1ms overhead)

**Response Format Change:**
```json
// Before
{"answer": "Treatment is X"}

// After
{
  "answer": "Treatment is X",
  "sources": [
    {
      "doc_id": "PubMed:12345678",
      "title": "Clinical Guidelines for X",
      "excerpt": "...",
      "relevance_score": 0.92,
      "source_type": "clinical_guideline"
    }
  ],
  "model_confidence": 0.87,
  "uncertainty_note": "Limited data on rare variants"
}
```

**Article Section Title:** *"Black Boxes Don't Work in Healthcare: Making RAG Transparent"*

---

## 📅 Development Timeline (HIS App)

### Phase 1: Foundation (Week 1–2)
**Goal:** Scaffold HIS backend + frontend, integrate with vector DB

- [ ] Create FastAPI project structure
- [ ] Set up Pydantic FHIR schemas (Patient, Observation, etc.)
- [ ] Create database layer (SQLite for patient data)
- [ ] Set up Qdrant + load medical knowledge base
- [ ] Install Ollama + download BioMistral-7B
- [ ] Create basic React frontend (forms + layout)
- [ ] Write docker-compose for local dev

**Deliverable:** Bare-bones HIS running locally (no AI yet)

---

### Phase 2: Core RAG Integration (Week 3–4)
**Goal:** Connect LLM + vector DB to create AI consultation feature

- [ ] Implement retrieval service (Qdrant queries)
- [ ] Integrate Ollama LLM inference
- [ ] Create consultation endpoint (`POST /consultations`)
- [ ] Implement response schema with citations
- [ ] Add confidence scoring
- [ ] Connect frontend to consultation API
- [ ] Test end-to-end query → LLM → response

**Deliverable:** Working AI consultation feature (single LLM)

---

### Phase 3: RAG Improvements (Week 5–6)
**Goal:** Add re-ranking, better relevance, production polish

- [ ] Implement BM25 re-ranking layer
- [ ] Benchmark: single-stage vs. two-stage retrieval
- [ ] Add model switching (BioMistral/Meditron/MedGemma) via `.env`
- [ ] Implement structured logging (production-grade)
- [ ] Add comprehensive error handling + validation
- [ ] Create test suite (unit + integration tests)
- [ ] Write API documentation (Swagger)

**Deliverable:** Production-ready backend with RAG improvements

---

### Phase 4: Polish + Testing (Week 7)
**Goal:** Quality assurance, documentation, deployment readiness

- [ ] Fix bugs from testing
- [ ] Improve frontend UX (error messages, loading states)
- [ ] Add sample data / demo consultations
- [ ] Performance testing (latency profiling)
- [ ] Write comprehensive README
- [ ] Create deployment guide
- [ ] Docker optimization (image size, startup time)

**Deliverable:** Portfolio-ready HIS app (can demo)

---

### Phase 5: Medium Article Extraction (Week 8)
**Goal:** Extract learnings into technical article

- [ ] Outline article: "Building a Healthcare RAG System"
- [ ] Document architecture decisions
- [ ] Benchmark results (RAG improvements)
- [ ] Code snippets + best practices
- [ ] Deploy article to Medium/TDS

**Deliverable:** Published article (~2500 words)

---

## 📂 Folder Structure (HIS App + RAG)

```
medical-his-rag/                      ← Main project repo
│
├── README.md                         ← Quick start guide
├── PROJECT.md                        ← This file
├── docker-compose.yml                ← Local dev setup (Qdrant + Ollama)
├── .env.example                      ← Environment variables
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  ← FastAPI entry point
│   │   ├── config.py                ← Config + settings
│   │   ├── schemas/                 ← FHIR Pydantic models
│   │   │   ├── patient.py           ← FHIR Patient schema
│   │   │   ├── consultation.py      ← Query input schema
│   │   │   ├── assessment.py        ← AI response schema
│   │   │   └── observation.py       ← Vital signs schema
│   │   ├── services/
│   │   │   ├── retriever.py         ← Vector search (Qdrant)
│   │   │   ├── llm_service.py       ← LLM inference (Ollama)
│   │   │   ├── reranker.py          ← BM25 re-ranking
│   │   │   ├── patient_service.py   ← Patient DB operations
│   │   │   └── consultation_service.py ← Consultation logic
│   │   ├── routers/
│   │   │   ├── health.py            ← /health endpoint
│   │   │   ├── patients.py          ← /patients/* endpoints
│   │   │   ├── consultations.py     ← /consultations/* endpoints
│   │   │   └── knowledge.py         ← /knowledge/* endpoints
│   │   ├── models/
│   │   │   └── database.py          ← SQLite models
│   │   ├── utils/
│   │   │   ├── logging_config.py    ← Structured logging
│   │   │   ├── exceptions.py        ← Custom exceptions
│   │   │   └── fhir_helpers.py      ← FHIR formatting
│   │   └── middleware/
│   │       ├── error_handler.py     ← Global error handling
│   │       └── logging_middleware.py ← Request/response logging
│   │
│   ├── tests/
│   │   ├── test_patient_api.py
│   │   ├── test_consultation_api.py
│   │   ├── test_rag.py
│   │   └── test_integration.py
│   │
│   ├── data/
│   │   ├── medical_knowledge.json   ← Pre-indexed documents
│   │   └── sample_patients.json     ← Demo data
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatientForm.jsx
│   │   │   ├── VitalsInput.jsx
│   │   │   ├── ConsultationResult.jsx
│   │   │   └── SourceCitations.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── PatientLookup.jsx
│   │   │   ├── NewConsultation.jsx
│   │   │   └── ConsultationHistory.jsx
│   │   ├── services/
│   │   │   └── api.js               ← Axios config
│   │   ├── App.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── Dockerfile
│
├── docs/
│   ├── ARCHITECTURE.md              ← System design
│   ├── API_SPECIFICATION.md         ← FHIR endpoints
│   ├── SETUP_GUIDE.md               ← Local development
│   ├── DEPLOYMENT.md                ← Docker deployment
│   └── MEDIUM_ARTICLE_OUTLINE.md    ← Future article
│
└── infra/
    ├── docker-compose.yml            ← Dev environment
    ├── docker-compose.prod.yml       ← Production (optional)
    └── .env.example
```

---

## 🔍 Key References & Research

### Critical Papers
1. **"When Retrieval Doesn't Help: A Large-Scale Study of Biomedical RAG"** (Rios et al., June 2026)
   - Finding: Retrieval improvements yield only 1–2% accuracy gains
   - LLM choice has larger effect than retriever choice
   - **Use in article:** Counter the "18% RAG improvement" hype

2. **"ModernBERT + ColBERT: Enhancing Biomedical RAG"** (Oct 2025)
   - Finding: Two-stage retrieval outperforms single-stage
   - Re-ranker improves precision@5 by ~3–5%
   - **Use in article:** Support your re-ranking improvement

3. **"BioMistral: A Collection of Open-Source LLMs"** (Feb 2024)
   - MedQA performance: ~60% (7B), ~72% (70B variants)
   - **Use in article:** Benchmark baseline

4. **"Healthcare LLM Landscape 2026"** (Nirmitee.io, Jan 2026)
   - MedGemma 1.5: ~91% MedQA (SOTA open-weight)
   - Meditron-70B: strong on guideline-grounded reasoning
   - **Use in article:** Model comparison context

### Existing Medical RAG Repos
- **iamaber/medical-guideline-rag** (~2.5K ⭐) — production-ready but API-dependent
- **fenil210/Medical-RAG** (~300 ⭐) — local-first, simpler codebase
- **slinusc/medical_RAG_system** (~400 ⭐) — research-focused
- **gzxiong/MedRAG** (~1.2K ⭐) — comprehensive toolkit

---

## ✍️ Article Structure (Skeleton)

### Title Options
1. "I Cloned a Medical RAG Repo and Made It 30% Faster — Here's What I Changed"
2. "Why Your Medical RAG System Gets 60% of Questions Wrong (And How to Fix It)"
3. "Reproducing a Popular Medical RAG GitHub Project and Fixing Its Gaps"

### Outline
```
1. Hook (300 words)
   - "I found a popular medical RAG repo with 300+ stars..."
   - "But when I benchmarked it, accuracy was only 58%"
   - "Here's what I fixed and what it cost"

2. Context: The RAG Hype vs. Reality (200 words)
   - Recent research shows retrieval isn't the bottleneck
   - LLM choice matters more
   - Most existing repos use old/API-dependent models

3. Problem #1: LLM Bottleneck (400 words)
   - Current: BioMistral-7B (58% MedQA)
   - Problem: Outdated model, lower benchmark
   - Experiment: Benchmarked Meditron, MedGemma
   - Table: accuracy/latency/cost tradeoff

4. Problem #2: Single-Stage Retrieval (300 words)
   - Current: Query → dense search → LLM
   - Problem: Relevant docs may be ranked low
   - Solution: Add re-ranking (ModernBERT pattern)
   - Benchmark: Precision@5, recall@10 improvement

5. Problem #3: Black-Box Answers (300 words)
   - Current: Returns answer only
   - Problem: Doctors won't trust without reasoning
   - Solution: Track sources + confidence scores
   - Example: Response JSON with citations

6. Benchmarks & Tradeoffs (400 words)
   - Table: Baseline vs. Improved version
   - Accuracy gain: ~5–10%
   - Latency cost: +50–200ms
   - VRAM cost: +10–25GB
   - When to use each

7. Discussion (300 words)
   - What surprised me in this project
   - Hidden complexity in "production-ready" repos
   - Open question: "Would you trade 200ms latency for 10% accuracy gain?"

8. References (100 words)
   - Rios et al. (2026)
   - ModernBERT + ColBERT (2025)
   - Original repo authors
   - GitHub link to your fork
```

---

## 📢 Content & Portfolio Plan

### Phase 1: Build HIS App (Private Portfolio)
- GitHub repo: `medical-his-rag` (public, production-ready code)
- Demo video: Video walkthrough of HIS in action
- README: Comprehensive setup + architecture
- **Goal:** Impress recruiters/clients with real working app

### Phase 2: Extract Medium Article
**After HIS is complete**, extract a technical article:

**Title:** "Building a Healthcare Information System with RAG: From Planning to Production"

**Content:**
1. Architecture decisions (why FastAPI, Qdrant, Ollama?)
2. Medical data standards (FHIR schemas in Pydantic)
3. RAG improvements (single-stage vs. two-stage retrieval)
4. Production patterns (error handling, logging, containerization)
5. Benchmarks (LLM comparison: BioMistral vs. MedGemma vs. Meditron)
6. Lessons learned + tradeoffs

**Target:** 2500-3000 words

### Publishing Strategy

#### 1. GitHub (Primary - Week 7)
- Publish full code: `medical-his-rag`
- Add MIT license
- Include comprehensive README
- Demo video link
- Expected reach: 50-200 stars (healthcare + backend audience)

#### 2. Medium/TDS (Secondary - Week 8)
- Submit article to Towards Data Science
- Link to GitHub repo
- Focus on technical depth (architecture + RAG)
- Tags: `Healthcare AI`, `RAG`, `FastAPI`, `Backend`, `Production`

#### 3. Portfolio Website
- Add project to portfolio site
- Link to GitHub + article
- Describe technical skills demonstrated

### Article Tags (TDS Format)
```
1. Healthcare AI          ← Primary niche
2. Retrieval Augmented Generation  ← TDS favorite
3. Backend Development    ← Shows full-stack skills
4. Production Systems     ← Practical, not academic
5. Python / FastAPI       ← Technical stack
```

### Expected Outcomes
- **GitHub stars:** 100-300 (if shared in communities)
- **Medium views:** 500-1000 (healthcare + backend audience)
- **Portfolio impact:** Strong technical credibility for job search

---

## 📊 Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| fenil210 repo already has your improvements | Low | High | Check latest commits first |
| LLM swap breaks the system | Medium | Medium | Test each model in isolation |
| Benchmark noise (unstable results) | Medium | Low | Run 3 random seeds, report mean ± std |
| TDS rejects article | Medium | Medium | Fallback to Towards AI (80%+ acceptance) |
| Knowledge base outdated mid-article | Low | Low | Use static snapshot; mention in article |

---

## ⚙️ Production-Ready Requirements

Every part of this app should demonstrate real backend engineering:

### Code Quality
- ✅ Type hints on all functions (Pydantic + Python typing)
- ✅ Comprehensive error handling (custom exceptions, graceful failures)
- ✅ Structured logging (not just print statements)
- ✅ Unit + integration tests
- ✅ API documentation (Swagger/OpenAPI)
- ✅ Docstrings on critical functions

### Data Handling
- ✅ FHIR-compliant schemas (using Pydantic)
- ✅ Input validation (reject invalid vital signs, etc.)
- ✅ Privacy-safe logging (never log PII)
- ✅ Database transactions (no data corruption)

### Deployment
- ✅ Dockerfile (multi-stage build, optimized image)
- ✅ Docker Compose (dev + optional prod)
- ✅ Health checks (FastAPI lifespan events)
- ✅ Environment config (.env file)
- ✅ README with clear setup instructions

### Performance
- ✅ Model quantization (4-bit, fits in 14GB VRAM)
- ✅ Latency tracking (response times < 2 sec)
- ✅ Memory profiling (no memory leaks)
- ✅ Caching where appropriate (embedding cache, etc.)

---

## 📝 Next Steps

### This Week (Week 1)
- [ ] **Review plan** with team
- [ ] **Create GitHub repo** (`medical-his-rag`) 
- [ ] **Set up project structure** from folder layout above
- [ ] **Install dependencies:** FastAPI, Pydantic, Qdrant, Ollama

### Week 1-2 (Foundation Phase)
- [ ] Scaffold FastAPI backend
- [ ] Create FHIR Pydantic schemas
- [ ] Set up SQLite for patients
- [ ] Create React frontend skeleton
- [ ] Write docker-compose.yml
- [ ] Get bare-bones app running locally

### Ongoing
- [ ] Push to GitHub weekly (WIP commits)
- [ ] Track progress in `/docs/PROGRESS.md`
- [ ] Test locally frequently (don't wait for "perfect" code)

---

## 🔗 Useful Resources

- **Ollama** (run models locally): https://ollama.ai/
- **HuggingFace Models:** 
  - BioMistral: https://huggingface.co/BioMistral/BioMistral-7B
  - Meditron: https://huggingface.co/epfl-llm/Meditron-70B
  - MedGemma: https://huggingface.co/google/medgemma-1.5-7b
- **MMLU-Med Benchmark:** https://github.com/openai/evals/blob/main/evals/registry/data/mmlu/mmlu_med.jsonl
- **fenil210/Medical-RAG:** https://github.com/fenil210/Medical-RAG

---

**Status:** ✅ Planning Phase Complete  
**Next Phase:** Implementation (Week 1–5)  
**Final Deliverable:** Medium Article + GitHub Code + Benchmarks

