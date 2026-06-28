# 📊 Benchmarking Plan & Methodology

## Benchmark Strategy

### Goal
Compare baseline (fenil210/Medical-RAG with BioMistral-7B) against each improvement to quantify:
- Accuracy gain
- Latency cost
- VRAM requirements
- Overall improvement viability

### Test Datasets

#### Primary: MMLU-Med Subset
```
Size: 30–50 questions
Source: MMLU Medical benchmark
Format:
{
  "question": "...",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "A",
  "category": "clinical_medicine",
  "difficulty": "intermediate"
}
```

**Why:** Medical-specific, standardized, reproducible

#### Secondary: Custom Medical Q&A
```
Create 10–15 additional questions from:
- Medical textbooks (Harrison's, Merck Manual)
- Clinical practice guidelines (WHO, NIH)
- Real physician queries (anonymized)

Example:
Q: "A 45-year-old male with HTN presents with dyspnea. BP 160/100, HR 110. 
    What is the most likely diagnosis?"
A: "Hypertensive emergency / Acute coronary syndrome"
```

---

## Measurement Metrics

### 1. Accuracy (Primary Metric)
```
Definition: % of questions answered correctly
Formula:    (Correct Answers / Total Questions) × 100

Baseline:   58% (BioMistral-7B)
Target:     72%+ (with LLM upgrade)
```

**How to measure:**
```python
def compute_accuracy(responses, ground_truth):
    correct = sum(1 for r, gt in zip(responses, ground_truth) if r == gt)
    return (correct / len(responses)) * 100
```

### 2. Latency (Secondary Metric)
```
Definition: Time from query submission to response generation
Measurement: p50 (median), p95 (95th percentile)

Baseline:   ~180ms (p50), ~220ms (p95) [BioMistral-7B]
Target:     <500ms (p95) [with Meditron-70B]

Why p95: Worst-case user experience matters more than average
```

**How to measure:**
```python
import time
import numpy as np

latencies = []
for query in test_set:
    start = time.time()
    response = model.generate(query)
    latency_ms = (time.time() - start) * 1000
    latencies.append(latency_ms)

p50 = np.percentile(latencies, 50)
p95 = np.percentile(latencies, 95)
```

### 3. Retrieval Quality (Improvement #2)
```
Definition: What fraction of top-K results are actually relevant?

Precision@5:
  Formula: (Relevant docs in top-5) / 5
  Baseline: ~0.60 (3 out of 5)
  Target:   ~0.75 (with re-ranker)

Recall@10:
  Formula: (Relevant docs in top-10) / (Total relevant docs)
  Baseline: ~0.70
  Target:   ~0.80 (with re-ranker)

MRR (Mean Reciprocal Rank):
  Formula: 1 / (position of first relevant doc)
  Baseline: ~0.50 (first relevant at position 2)
  Target:   ~0.67 (first relevant at position 1.5)
```

**Relevance Assessment:**
```
Manual annotation:
  Relevant (score=1):   Directly addresses query
  Partially (score=0.5): Addresses related aspect
  Irrelevant (score=0):  Unrelated to query

Example:
Query: "What is the treatment for diabetes type 2?"
Top-5 results:
  1. "Metformin in T2DM" → Relevant (score=1) ✓
  2. "Insulin analogues" → Relevant (score=1) ✓
  3. "Type 1 diabetes overview" → Partially (score=0.5) ~
  4. "Glucose metabolism" → Irrelevant (score=0) ✗
  5. "Diabetic complications" → Partially (score=0.5) ~
  
Precision@5 = 2.5 / 5 = 0.50
```

### 4. Confidence Calibration (Improvement #3)
```
Definition: Is the model's stated confidence aligned with actual accuracy?

Expected Calibration Error (ECE):
  ECE = avg |Confidence - Accuracy| across confidence buckets
  
Example:
  Confidence [0.8–0.9]: Model says 85% confident
                        But only gets 78% right
                        Error: |0.85 - 0.78| = 0.07
  
  Target: ECE < 0.10 (well-calibrated)
```

**How to measure:**
```python
def compute_calibration_error(confidences, accuracies, n_bins=10):
    """
    Split into n_bins based on confidence.
    For each bin, compute |avg_confidence - avg_accuracy|
    """
    import numpy as np
    
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0
    
    for i in range(n_bins):
        mask = (confidences >= bins[i]) & (confidences < bins[i+1])
        if mask.sum() == 0:
            continue
        
        bin_conf = confidences[mask].mean()
        bin_acc = accuracies[mask].mean()
        ece += abs(bin_conf - bin_acc) * mask.sum() / len(confidences)
    
    return ece
```

---

## Benchmark Execution Plan

### Phase 1: Baseline (Week 1–2)
```
1. Prepare test set (30 MMLU-Med questions + 10 custom)
2. Run BioMistral-7B on all 40 questions
3. Measure accuracy, latency (p50/p95), VRAM usage
4. Save baseline results to `benchmark_results/baseline.json`
```

**Baseline Results Format:**
```json
{
  "model": "BioMistral-7B",
  "test_set_size": 40,
  "results": {
    "accuracy": 0.58,
    "latency_p50_ms": 180,
    "latency_p95_ms": 220,
    "vram_gb": 13
  },
  "timestamp": "2026-07-04T12:34:56Z"
}
```

### Phase 2: Improvement #1 — LLM Upgrades (Week 2–3)
```
Models to benchmark:
  1. Meditron-70B (requires 40GB VRAM)
  2. MedGemma-7B (requires 14GB VRAM)
  
For each model:
  - Run same 40 questions
  - Measure accuracy, latency, VRAM
  - Save to `benchmark_results/[model_name].json`
  - Create comparison table
```

**Comparison Table Example:**
```markdown
| Model | Accuracy | Latency p50 | Latency p95 | VRAM | Accuracy Gain |
|-------|----------|-------------|-------------|------|---------------|
| BioMistral-7B | 58% | 180ms | 220ms | 13GB | — |
| MedGemma-7B | 72% | 220ms | 280ms | 14GB | +14% |
| Meditron-70B | 72% | 450ms | 580ms | 38GB | +14% |
```

### Phase 3: Improvement #2 — Re-ranker (Week 3–4)
```
For each LLM (BioMistral, MedGemma):
  - Run with BM25 re-ranker enabled
  - Measure: Precision@5, Recall@10, MRR
  - Measure: Overall accuracy change
  - Measure: Latency impact (add ~50ms)
```

**Re-ranking Comparison:**
```
BioMistral-7B Without Re-ranker:
  - Accuracy: 58%
  - Precision@5: 0.60
  - MRR: 0.50
  - Latency: 180ms

BioMistral-7B With Re-ranker:
  - Accuracy: 60% (+2%)
  - Precision@5: 0.75 (+0.15)
  - MRR: 0.67 (+0.17)
  - Latency: 230ms (+50ms)
```

### Phase 4: Improvement #3 — Citations (Week 4–5)
```
For the chosen LLM + re-ranker combo:
  - Enable citation tracking
  - Verify all responses have sources
  - Measure confidence calibration (ECE)
  - Verify response latency overhead <10ms
```

**Citation Verification Checklist:**
```
✓ For each query result:
  - ✓ sources array is populated
  - ✓ Each source has doc_id, title, excerpt
  - ✓ Relevance score is between 0.0 and 1.0
  - ✓ Source type is one of: clinical_guideline, research_article, textbook
  - ✓ Confidence score is computed
  - ✓ Confidence <= avg(source relevance scores)
  
✓ Confidence Calibration:
  - ✓ ECE < 0.10 (well-calibrated)
  - ✓ High-confidence answers (0.8+) > 75% accurate
  - ✓ Low-confidence answers (0.5-0.6) < 60% accurate
```

### Phase 5: Final Integration (Week 5)
```
Deploy all improvements together:
  - LLM: MedGemma-7B (or chosen model)
  - Retriever: With BM25 re-ranker
  - Response: With citations + confidence
  
Run full test set (40 questions):
  - Measure combined improvement
  - Latency breakdown: retrieval vs. LLM vs. re-rank
  - Final accuracy: target 70%+
```

---

## Expected Results & Confidence Intervals

### LLM Upgrade (Improvement #1)
```
Expected Outcome:
  BioMistral-7B:  58% accuracy ± 5%
  MedGemma-7B:    72% accuracy ± 4%  [+14% expected]
  Meditron-70B:   72% accuracy ± 4%  [+14% expected]

Why confidence intervals exist:
  - Test set randomness (only 40 questions)
  - Model stochasticity (temperature > 0)
  - Annotation ambiguity for edge cases
```

### Re-ranking (Improvement #2)
```
Expected Outcome:
  Precision@5:    +0.15 improvement (0.60 → 0.75)
  Recall@10:      +0.10 improvement (0.70 → 0.80)
  Accuracy lift:  +0.5% to +2% (small but real)
  Latency cost:   +50ms
```

### Citations (Improvement #3)
```
Expected Outcome:
  Citation Coverage: 100% (all responses have sources)
  Confidence ECE:    ~0.05–0.08 (well-calibrated)
  Latency overhead:  <10ms
```

### Combined Improvements
```
Baseline (BioMistral-7B only):
  - Accuracy: 58%
  - Latency: 180ms (p50)
  - Sources: None
  - Confidence: N/A

Improved (MedGemma-7B + re-ranker + citations):
  - Accuracy: 70–75%
  - Latency: 270ms (p50)
  - Sources: 100% coverage
  - Confidence: Well-calibrated (ECE < 0.08)

Improvement Summary:
  - Accuracy gain: +12–17%
  - Latency cost: +90ms (50% slower, still acceptable)
  - New capabilities: Citations, confidence scores
```

---

## Reporting Format

### For Article
```markdown
## Benchmarks: Baseline vs. Improved

### Test Methodology
- Test Set: 30 MMLU-Med + 10 custom questions
- Evaluation: Accuracy, latency, retrieval quality
- Infrastructure: Single GPU (RTX 4090)

### Results

| Aspect | Baseline | With Improvements | Change |
|--------|----------|------------------|--------|
| **Accuracy** | 58% | 72% | +14% |
| **Latency (p50)** | 180ms | 270ms | +90ms |
| **Precision@5** | 0.60 | 0.75 | +0.15 |
| **Citations** | None | 100% | ✓ |

### Tradeoffs
- **Accuracy vs. Speed:** +14% accuracy costs +90ms latency
- **Resources:** Improved system needs 14GB VRAM (vs. 13GB baseline)
- **Recommendation:** Worth it for medical use cases (accuracy > speed)
```

### For GitHub
```
benchmarks/
├── baseline.json           ← BioMistral-7B results
├── medgemma.json          ← MedGemma-7B results
├── meditron.json          ← Meditron-70B results
├── with_reranker.json     ← Re-ranking addition
├── with_citations.json    ← Citations addition
└── summary_table.md       ← Comparison table
```

---

## Continuous Monitoring (Post-Publication)

### If Article Gets Traction
```
- Monitor reader questions in comments
- Add new test cases based on reader feedback
- Re-benchmark on larger dataset (100+ questions)
- Update results if models change (new versions)
```

### Version Tracking
```
Benchmark Version: 1.0 (June 2026)
  - 40 questions
  - BioMistral, MedGemma, Meditron
  - Published in Medium article

Benchmark Version: 1.1 (July 2026, if needed)
  - Expanded to 100 questions (based on feedback)
  - Include Llama 3.1 results
  - Add multimodal retrieval results
```

---

**Status:** Benchmarking plan documented  
**Next:** Execute Phase 1–2 (Weeks 1–3)
