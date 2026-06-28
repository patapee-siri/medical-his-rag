# 🏗️ Medical RAG Architecture Overview

## Current System (fenil210/Medical-RAG)

### High-Level Flow
```
User Query
    ↓
[Preprocessing Layer]
  - Tokenization
  - Lowercasing
  - Special character handling
    ↓
[Retrieval Layer]
  - Query → Dense Embedding (Pubmed-BERT)
  - FAISS/Qdrant Vector Search
  - Top-K retrieval (k=5-10)
    ↓
[Chunking & Assembly]
  - Semantic chunking (overlap handling)
  - Context window assembly
    ↓
[Generation Layer]
  - BioMistral-7B (quantized to 4-bit)
  - FastAPI endpoint
  - Streaming response
    ↓
User Answer
```

### Component Breakdown

#### 1. Knowledge Base
- **Source:** PubMed-licensed medical documents
- **Format:** Chunked text + embeddings (pre-computed)
- **Vector DB:** Qdrant (Docker containerized)
- **Embedding Model:** PubMed-BERT (768 dimensions)
- **Size:** ~2.4M PubMed abstracts (subset)

#### 2. Retriever
```python
# Pseudocode
query_embedding = pubmed_bert_encoder(user_query)
candidates = qdrant.search(
    vector=query_embedding,
    top_k=10,
    threshold=0.5  # similarity threshold
)
context = concatenate(candidates.text)
```

**Current Limitations:**
- ❌ Single-stage retrieval (no re-ranking)
- ❌ Cosine similarity only (no learned ranking)
- ❌ No query expansion or reformulation
- ❌ No result deduplication

#### 3. LLM Inference
```python
# Pseudocode
prompt = f"""
Based on these documents:
{context}

Answer the question: {user_query}
"""

response = biomistr al_7b.generate(
    prompt,
    max_tokens=256,
    temperature=0.7
)
```

**Current Setup:**
- Model: BioMistral-7B (7B parameters)
- Quantization: 4-bit (13GB VRAM)
- Framework: Transformers + vLLM (for serving)
- API: FastAPI with streaming

**Bottleneck:** BioMistral-7B achieves only ~58% on MedQA benchmark

---

## Proposed Improvements

### Improvement #1: LLM Upgrade Path

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ Model               │ MedQA Score  │ VRAM (4-bit) │ Latency      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ BioMistral-7B       │ ~58%         │ 13GB         │ 180ms        │
│ MedGemma-7B (NEW)   │ ~72%         │ 14GB         │ 220ms        │
│ Meditron-70B (NEW)  │ ~72%         │ 38GB         │ 450ms        │
└─────────────────────┴──────────────┴──────────────┴──────────────┘
```

**Implementation:**
```python
# Option A: Via Ollama (simplest)
import ollama
response = ollama.generate(
    model="meditron:70b-4bit",  # auto-quantizes
    prompt=prompt
)

# Option B: Via HuggingFace (more control)
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "epfl-llm/Meditron-70B",
    load_in_4bit=True,
    device_map="auto"
)
```

**Tradeoff Decision Matrix:**
```
            Accuracy Gain  Latency Cost  VRAM Cost  Best For
MedGemma    +14%           +40ms         +1GB       Balanced
Meditron    +14%           +270ms        +25GB      Guideline-grounded
```

---

### Improvement #2: Two-Stage Retriever Architecture

**Current (Single-Stage):**
```
Query
  → Embed (PubMed-BERT)
  → Vector search (cosine similarity)
  → Top-10 results
  → LLM
```

**Proposed (Two-Stage with Re-ranking):**
```
Query
  → Embed (PubMed-BERT)
  → Vector search (dense, get top-50)
  → [NEW] Neural Re-ranker (ColBERT-style)
     - Score all 50 candidates with learned ranker
     - Re-sort by learned relevance
     - Keep top-10
  → LLM
```

#### Re-ranker Options

**Option A: Simple BM25 Second Stage**
```python
# Pseudocode: BM25 re-ranking
bm25_scores = bm25_model.score_batch(query, candidates)
reranked = sorted(candidates, key=bm25_scores, reverse=True)[:10]
```
- Pros: Fast (~10ms), no training needed
- Cons: Lexical only, less accurate

**Option B: Fine-tuned ColBERT-style Re-ranker**
```python
# Pseudocode: Neural re-ranking
reranker = ColBERT(checkpoint="medical-reranker-v1")
scores = reranker.score_batch(query, candidates)
reranked = sorted(candidates, key=scores, reverse=True)[:10]
```
- Pros: Semantic understanding, learned relevance
- Cons: Requires training or fine-tuned checkpoint (~30–50ms per query)

**Metrics to Track:**
- Precision@5: % of top-5 results actually relevant
- Recall@10: % of all relevant docs in top-10
- MRR (Mean Reciprocal Rank): Position of first relevant doc

**Expected Improvement:** +0.5–1% accuracy, +50ms latency

---

### Improvement #3: Explainability & Citation Layer

**Current Response:**
```json
{
  "answer": "The treatment involves X and Y",
  "processing_time_ms": 245
}
```

**Proposed Response:**
```json
{
  "answer": "The treatment involves X and Y",
  "sources": [
    {
      "doc_id": "PubMed:12345678",
      "title": "Clinical Practice Guidelines for Disease X",
      "authors": ["Smith, J.", "Brown, K."],
      "year": 2023,
      "excerpt": "Treatment should include X and Y as first-line therapy",
      "relevance_score": 0.92,
      "source_type": "clinical_guideline",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    },
    {
      "doc_id": "PubMed:87654321",
      "title": "Randomized Controlled Trial of X in Disease Y",
      "authors": ["Doe, A.", "Jones, B."],
      "year": 2024,
      "excerpt": "X demonstrated 85% efficacy rate in our cohort",
      "relevance_score": 0.87,
      "source_type": "research_article"
    }
  ],
  "model_confidence": 0.87,
  "uncertainty_notes": [
    "Limited pediatric data available",
    "Results may vary by region"
  ],
  "processing_time_ms": 245
}
```

#### Implementation

**Schema Changes:**
```python
from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    doc_id: str
    title: str
    authors: List[str]
    year: int
    excerpt: str
    relevance_score: float  # 0.0 to 1.0
    source_type: str  # "clinical_guideline", "research_article", etc.
    url: Optional[str]

class RAGResponse(BaseModel):
    answer: str
    sources: List[Source]
    model_confidence: float
    uncertainty_notes: List[str]
    processing_time_ms: int
```

**Retriever Metadata Tracking:**
```python
# Store metadata with each chunk during indexing
chunk_data = {
    "id": "PubMed:12345678",
    "text": "...",
    "metadata": {
        "doc_title": "...",
        "doc_authors": [...],
        "pub_year": 2023,
        "source_type": "clinical_guideline",
        "url": "..."
    }
}

qdrant.upsert(points=[...with metadata...])
```

**Confidence Calibration:**
```python
# Simple approach: Use retriever scores
avg_relevance = mean([s.relevance_score for s in sources])
model_confidence = min(avg_relevance, 0.95)  # Cap at 0.95 (never fully certain)

# Advanced approach: Temperature-based confidence
# Higher temperature → lower confidence
# Lower temperature → higher confidence
```

---

## Data Flow Diagram (ASCII)

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INPUT QUERY                           │
│                   "How do I treat X?"                         │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│               PREPROCESSING (Query Encoding)                  │
│  - Tokenize                                                   │
│  - Normalize                                                  │
│  - Generate embedding via PubMed-BERT                         │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│            STAGE 1: DENSE RETRIEVAL (Qdrant)                 │
│  - Vector similarity search                                   │
│  - Top-50 candidates by cosine similarity                     │
│  - Time: ~20ms                                                │
└────────────────────────────┬─────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
        [CURRENT SYSTEM]        [IMPROVEMENT #2]
        (Single-stage)          (Add Re-ranker)
        │                       │
        │ Top-10              │ Score 50 with BM25
        │                       │ Re-sort
        │                       │ Top-10
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────────────────┐
│            CONTEXT ASSEMBLY (Chunking)                        │
│  - Deduplicate overlapping chunks                             │
│  - Assemble into prompt context (~2000 tokens max)           │
│  - Time: ~5ms                                                 │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│        GENERATION (LLM Inference + Citations)                │
│  [CURRENT] BioMistral-7B                                     │
│  [IMPROVEMENT #1] Swap to Meditron-70B or MedGemma-7B        │
│  - Encode: context + query into prompt                        │
│  - Generate: answer tokens                                    │
│  - [NEW] Track which chunks contributed to answer             │
│  - Time: ~180–450ms (depends on LLM)                          │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│        POSTPROCESSING (Response Formatting)                   │
│  - Extract answer text                                        │
│  - [NEW] Compute model_confidence (avg relevance)            │
│  - [NEW] Format sources as structured JSON                    │
│  - [NEW] Add uncertainty_notes                                │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                      USER RESPONSE                            │
│  {                                                            │
│    "answer": "...",                                           │
│    "sources": [...],     ← [NEW]                             │
│    "confidence": 0.87,   ← [NEW]                             │
│    "processing_time_ms": 245                                  │
│  }                                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Bottleneck Analysis (Latency Breakdown)

### Current System (BioMistral-7B)
```
Query Processing:     5ms
  ├─ Tokenization     1ms
  └─ Embedding        4ms

Retrieval:           20ms
  ├─ Vector search   15ms
  └─ Chunk fetch     5ms

LLM Inference:      180ms
  ├─ Prompt build    5ms
  └─ Token generation 175ms (7B @ 40 tokens/sec)

Response Formatting: 5ms

TOTAL:               210ms
```

### With Improvements
```
Query Processing:     5ms (no change)
Retrieval Stage 1:   20ms (no change)
Retrieval Stage 2:   50ms (NEW re-ranker)
LLM Inference:      450ms (Meditron-70B: slower)
Response Formatting: 10ms (NEW citations)

TOTAL:               535ms
```

**Tradeoff:** +325ms latency for ~14% accuracy improvement

---

## Testing & Validation Strategy

### Unit Tests
```
✓ Retrieval: Does it return top-K relevant chunks?
✓ Re-ranker: Does it improve precision@5?
✓ Confidence: Is it calibrated (high confidence → high accuracy)?
✓ Citations: Are metadata fields populated correctly?
```

### Integration Tests
```
✓ End-to-end: Query → Answer + Sources
✓ Latency: Is it within acceptable range?
✓ Memory: Does quantized model fit in VRAM?
```

### Benchmarking
```
Metrics:
  - Accuracy on MMLU-Med subset
  - Latency (p50, p95)
  - Precision@5 (retrieval quality)
  - Calibration error (confidence vs. actual accuracy)

Baselines:
  - Original fenil210 system
  - Your improved system
  - Paper baselines (MedRAG, MIRAGE)
```

---

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Embedding** | PubMed-BERT | HF checkpoint |
| **Vector DB** | Qdrant | 1.7+ (Docker) |
| **LLM Base** | HuggingFace Transformers | 4.30+ |
| **LLM Serving** | vLLM or Ollama | Latest |
| **API Framework** | FastAPI | 0.95+ |
| **Quantization** | bitsandbytes | 0.41+ |
| **Retriever Re-rank** | ColBERT or BM25 | TBD |
| **Inference Server** | Docker | Latest |

---

## File Structure (Code)

```
fenil210/Medical-RAG/
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI entry point
│   │   ├── retriever.py        ← Qdrant queries
│   │   ├── llm_service.py      ← LLM calls [IMPROVE #1]
│   │   ├── reranker.py         ← [NEW] Re-ranking logic
│   │   └── response_builder.py ← [NEW] Citations + confidence
│   ├── config.py
│   └── requirements.txt
├── data/
│   └── embeddings/             ← Pre-computed Qdrant indexes
└── docker-compose.yml          ← Qdrant container
```

---

**Status:** Architecture documented  
**Next:** See `IMPROVEMENTS.md` for detailed implementation plan
