# 📋 Medical HIS API Specification (FHIR-Compliant)

**Status:** Planning  
**Last Updated:** June 28, 2026  
**Standard:** FHIR R4 (Health Level 7)

---

## 🔑 Core Endpoints

### 1. Health Check
```http
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "database": "ok",
    "vector_db": "ok",
    "llm": "ok"
  },
  "timestamp": "2026-06-28T14:30:00Z"
}
```

---

## 👥 Patient Management

### Create Patient
```http
POST /patients
Content-Type: application/json
```

**Request:**
```json
{
  "name": "John Doe",
  "date_of_birth": "1980-06-15",
  "gender": "male",
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "medical_history": [
    {
      "condition": "Hypertension",
      "onset_date": "2020-01-01",
      "status": "active"
    },
    {
      "condition": "Type 2 Diabetes",
      "onset_date": "2022-06-01",
      "status": "active"
    }
  ],
  "allergies": [
    {
      "substance": "Penicillin",
      "reaction": "anaphylaxis"
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "patient_id": "P-20260628-001",
  "resource_type": "Patient",
  "name": "John Doe",
  "date_of_birth": "1980-06-15",
  "gender": "male",
  "created_at": "2026-06-28T14:30:00Z",
  "fhir_reference": "Patient/P-20260628-001"
}
```

---

### Get Patient
```http
GET /patients/{patient_id}
```

**Response:** `200 OK`
```json
{
  "patient_id": "P-20260628-001",
  "resource_type": "Patient",
  "name": "John Doe",
  "date_of_birth": "1980-06-15",
  "gender": "male",
  "active_conditions": 2,
  "last_consultation": "2026-06-28T10:15:00Z"
}
```

---

### List Patients
```http
GET /patients?page=1&limit=20&search=John
```

**Response:** `200 OK`
```json
{
  "total": 145,
  "page": 1,
  "limit": 20,
  "results": [
    {
      "patient_id": "P-20260628-001",
      "name": "John Doe",
      "age": 45,
      "active": true
    }
  ]
}
```

---

## 🏥 Consultation (Main RAG Feature)

### Create Consultation (Query Medical Question)
```http
POST /consultations
Content-Type: application/json
```

**Request:**
```json
{
  "patient_id": "P-20260628-001",
  "chief_complaint": "Persistent headache and fever for 3 days",
  "vital_signs": {
    "blood_pressure": "140/90",
    "systolic_bp": 140,
    "diastolic_bp": 90,
    "heart_rate": 95,
    "temperature_celsius": 38.5,
    "respiratory_rate": 18,
    "oxygen_saturation": 98
  },
  "additional_symptoms": [
    "nausea",
    "sensitivity to light",
    "neck stiffness"
  ],
  "current_medications": [
    {
      "medication": "Lisinopril",
      "dosage": "10mg",
      "frequency": "once daily"
    }
  ],
  "recent_travel": false,
  "exposure_history": "none",
  "model_preference": "medgemma:7b-4bit"
}
```

**Response:** `200 OK` (or `202 Accepted` for async processing)
```json
{
  "consultation_id": "C-20260628-001",
  "patient_reference": "Patient/P-20260628-001",
  "created_at": "2026-06-28T14:30:00Z",
  "query_received": {
    "chief_complaint": "Persistent headache and fever for 3 days",
    "vital_signs": {...},
    "additional_symptoms": [...]
  },
  "ai_assessment": {
    "status": "COMPLETED",
    "primary_impression": "Clinical presentation suggests possible viral meningitis or severe migraine with fever. Concerning features include fever, headache, photophobia, and neck stiffness (possible meningeal signs).",
    "differential_diagnoses": [
      {
        "diagnosis": "Viral Meningitis",
        "probability": "HIGH",
        "confidence": 0.92,
        "reasoning": "Classic triad of fever, headache, and photophobia; neck stiffness is a red flag"
      },
      {
        "diagnosis": "Bacterial Meningitis",
        "probability": "MEDIUM",
        "confidence": 0.78,
        "reasoning": "Fever + severe headache, but lack of petechial rash makes less likely"
      },
      {
        "diagnosis": "Migraine with Aura + Fever",
        "probability": "LOW",
        "confidence": 0.55,
        "reasoning": "Possible but fever + meningeal signs less compatible"
      }
    ]
  },
  "recommendations": [
    {
      "recommendation_id": "REC-001",
      "priority": "CRITICAL",
      "action": "Immediate medical evaluation recommended",
      "urgency": "STAT",
      "reasoning": "Meningeal signs require emergency assessment and possible CSF analysis",
      "evidence": [
        {
          "document_title": "Meningitis - Emergency Department Guidelines",
          "source_type": "clinical_guideline",
          "relevance_score": 0.96,
          "key_excerpt": "Any patient presenting with fever + headache + altered mental status should be evaluated for meningitis. Lumbar puncture is diagnostic standard."
        }
      ]
    },
    {
      "recommendation_id": "REC-002",
      "priority": "HIGH",
      "action": "Obtain vital signs monitoring",
      "urgency": "IMMEDIATE",
      "reasoning": "Fever and tachycardia suggest infectious process"
    },
    {
      "recommendation_id": "REC-003",
      "priority": "HIGH",
      "action": "Consider empiric antimicrobial therapy",
      "urgency": "WITHIN 1 HOUR",
      "reasoning": "If meningitis suspected, empiric therapy should not be delayed for imaging",
      "contraindications": [
        {
          "medication": "Penicillin",
          "reason": "Patient allergy documented (anaphylaxis)"
        }
      ]
    }
  ],
  "sources": [
    {
      "source_id": "SRC-001",
      "title": "Meningitis: Clinical Features and Diagnosis",
      "authors": ["Smith, J.", "Johnson, K."],
      "publication_year": 2024,
      "source_type": "clinical_guideline",
      "document_id": "PubMed:35234567",
      "relevance_score": 0.96,
      "excerpt": "The classic triad of fever, headache, and neck stiffness should raise concern for meningitis...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/35234567/",
      "citation_formatted": "[1] Smith J, Johnson K. Meningitis: Clinical Features and Diagnosis. 2024."
    },
    {
      "source_id": "SRC-002",
      "title": "Differential Diagnosis of Acute Headache with Fever",
      "authors": ["Brown, A.", "Davis, M."],
      "publication_year": 2023,
      "source_type": "research_article",
      "document_id": "PubMed:36789012",
      "relevance_score": 0.89,
      "excerpt": "Fever + headache represents a medical emergency until meningitis is ruled out...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/36789012/"
    }
  ],
  "confidence_metrics": {
    "overall_confidence": 0.87,
    "explanation": "Confidence score derived from average relevance of evidence sources and model uncertainty",
    "calibration_info": "HIGH confidence predictions (>0.85) are typically accurate 85%+ of the time"
  },
  "uncertainty_and_limitations": [
    "Assessment based on reported symptoms only; physical exam findings (meningeal signs) need verification",
    "CSF analysis is the diagnostic gold standard and is not available from this RAG system",
    "Recent travel history and exposure details would improve differential diagnosis",
    "Limited pediatric-specific data if patient age is <18 years"
  ],
  "clinical_decision_support": {
    "next_steps": [
      "Urgent hospital evaluation (ED assessment)",
      "Consider CT head before LP if increased ICP risk",
      "CBC, CMP, blood cultures before antibiotics",
      "Lumbar puncture for CSF analysis (if no contraindications)"
    ],
    "red_flags": [
      "Neck stiffness (possible meningeal signs)",
      "High fever (38.5°C)",
      "Photophobia"
    ],
    "monitoring": [
      "Vital signs q15min initially",
      "Neurological status changes",
      "Rash development"
    ]
  },
  "metadata": {
    "model_used": "medgemma:7b-4bit",
    "retrieval_method": "two-stage (dense + BM25 re-ranking)",
    "documents_retrieved": 15,
    "documents_used": 3,
    "response_time_ms": 1240,
    "inference_time_ms": 950,
    "retrieval_time_ms": 150,
    "processing_timestamp": "2026-06-28T14:30:00Z"
  },
  "disclaimer": "This is an AI-assisted decision support tool. It should NOT replace professional medical judgment. All recommendations must be reviewed and approved by a licensed healthcare provider."
}
```

---

### Get Consultation History
```http
GET /consultations/{patient_id}?limit=10&offset=0
```

**Response:** `200 OK`
```json
{
  "patient_id": "P-20260628-001",
  "total_consultations": 23,
  "consultations": [
    {
      "consultation_id": "C-20260628-001",
      "created_at": "2026-06-28T14:30:00Z",
      "chief_complaint": "Persistent headache and fever for 3 days",
      "primary_impression": "Possible viral meningitis or severe migraine",
      "confidence": 0.87
    },
    {
      "consultation_id": "C-20260627-005",
      "created_at": "2026-06-27T10:15:00Z",
      "chief_complaint": "Type 2 Diabetes management",
      "primary_impression": "Current therapy is appropriate",
      "confidence": 0.91
    }
  ]
}
```

---

### Get Single Consultation Detail
```http
GET /consultations/detail/{consultation_id}
```

**Response:** `200 OK`
(Same as Create Consultation response above)

---

## 📚 Knowledge Base Management

### Search Medical Knowledge
```http
POST /knowledge/search
Content-Type: application/json
```

**Request:**
```json
{
  "query": "meningitis treatment guidelines",
  "top_k": 5,
  "retrieval_method": "dense",
  "filters": {
    "source_type": "clinical_guideline",
    "min_year": 2022
  }
}
```

**Response:** `200 OK`
```json
{
  "query": "meningitis treatment guidelines",
  "total_results": 47,
  "retrieved": 5,
  "documents": [
    {
      "doc_id": "PubMed:35234567",
      "title": "Meningitis: Clinical Features and Diagnosis",
      "authors": ["Smith, J.", "Johnson, K."],
      "year": 2024,
      "source_type": "clinical_guideline",
      "similarity_score": 0.94,
      "excerpt": "The classic triad of fever, headache, and neck stiffness should raise concern for meningitis...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/35234567/"
    }
  ],
  "retrieval_stats": {
    "retrieval_method_used": "dense",
    "dense_search_time_ms": 25,
    "reranking_time_ms": 0,
    "total_time_ms": 25
  }
}
```

---

### Get Knowledge Base Stats
```http
GET /knowledge/stats
```

**Response:** `200 OK`
```json
{
  "total_documents": 24532,
  "total_embeddings": 245320,
  "vector_db": "qdrant",
  "embedding_model": "pubmed-bert",
  "indexed_categories": [
    "cardiology",
    "neurology",
    "infectious_disease",
    "general_medicine"
  ],
  "last_updated": "2026-06-28T00:00:00Z"
}
```

---

## ⚠️ Error Responses

### Common HTTP Status Codes

```
400 Bad Request     - Invalid input (malformed vital signs, etc.)
401 Unauthorized    - Missing API key
403 Forbidden       - Not authorized for this resource
404 Not Found       - Patient/consultation not found
409 Conflict        - Resource already exists
422 Unprocessable   - Validation error on FHIR schema
500 Server Error    - Internal server error
503 Unavailable     - LLM or Qdrant service down
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid vital signs provided",
    "details": [
      {
        "field": "blood_pressure",
        "error": "Systolic BP must be between 0 and 300 mmHg",
        "value": 999
      }
    ],
    "timestamp": "2026-06-28T14:30:00Z",
    "request_id": "req-abc123"
  }
}
```

---

## 🔒 Security & Privacy

### Authentication
- API Key (Bearer token) in `Authorization` header
- CORS enabled (frontend origin only)
- Rate limiting: 100 req/min per API key

### Data Privacy
- No patient PII in logs
- Consultation responses marked as confidential
- HIPAA-relevant audit trails
- All responses include disclaimer

### Example Request with Auth:
```http
POST /consultations
Authorization: Bearer sk-medical-his-abc123xyz789
Content-Type: application/json

{...payload...}
```

---

## 📊 Pagination

All list endpoints support:
```
?page=1&limit=20&sort=-created_at&search=query
```

---

## 🧪 Testing

### Health Check (No Auth Required)
```bash
curl http://localhost:8000/health
```

### Create Patient
```bash
curl -X POST http://localhost:8000/patients \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @patient.json
```

### Create Consultation
```bash
curl -X POST http://localhost:8000/consultations \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d @consultation.json
```

---

**Next:** Implement these endpoints in FastAPI with full validation & error handling
