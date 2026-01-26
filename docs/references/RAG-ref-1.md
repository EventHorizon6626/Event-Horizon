# RAG Techniques - Complete Guide

## 🌱 FOUNDATIONAL RAG 

### 1. Simple RAG
The most basic approach for beginners — retrieve then pass to LLM for answering.

**Implementation:** simple query + incremental learning.

### 2. Simple RAG using a CSV file
Use CSV to create a simple Q&A system.

**Implementation:** embedding from CSV rows + Q&A pipeline.

### 3. Reliable RAG
Increase Simple RAG accuracy through validation & refinement.

**Implementation:** relevance checking + highlight passages used to answer.

### 4. Choose Chunk Size
Select optimal chunk size.

**Implementation:** experiment with multiple sizes to balance context & performance.

### 5. Proposition Chunking
Decompose text into factual sentences — extremely effective for legal systems, reports, administrative documents.

**Implementation:** LLM generates propositions → quality grading → store in vectorstore.

---

## 🔍 QUERY ENHANCEMENT — QUERY OPTIMIZATION

### 6. Query Transformations
Rewriting, step-back prompting, sub-query decomposition.

### 7. Hypothetical Questions (HyDE Approach)
Generate hypothetical questions → improve matching between query & data.

---

## 📚 CONTEXT & CONTENT ENRICHMENT

### 8. Hypothetical Prompt Embeddings (HyPE)
Precompute hypothetical prompts → faster & more accurate retrieval than HyDE.

No LLM cost at query time.

### 9. Contextual Chunk Headers
Add headers to chunks to increase understanding.

### 10. Relevant Segment Extraction (RSE)
Combine multiple chunks into long relevant segments → give LLM complete context.

### 11. Context Enrichment Techniques
Sentence-level embedding + retrieve adjacent sentences.

### 12. Semantic Chunking
Split by semantics instead of fixed length.

### 13. Contextual Compression
Compress chunks using LLM, retain important information.

### 14. Document Augmentation (Question Generation)
Generate additional related questions for each passage → increase hit rate.

---

## 🚀 ADVANCED RETRIEVAL

### 15. Fusion Retrieval
Combine keyword search + vector search.

### 16. Intelligent Reranking
LLM-based scoring, cross-encoder, metadata ranking.

### 17. Multi-faceted Filtering
Filters by metadata, content, similarity threshold, diversity.

### 18. Hierarchical Indices
Multi-level indexing: summaries → detailed chunks.

### 19. Ensemble Retrieval
Combine multiple embedding models & multiple algorithms.

### 20. Dartboard Retrieval
Optimize relevance + diversity simultaneously.

### 21. Multi-modal Retrieval
Combine text + captioning + image-based retrieval.

---

## 🔁 ITERATIVE & ADAPTIVE RAG

### 22. Retrieval with Feedback Loops
Learn from user feedback.

### 23. Adaptive Retrieval
Automatically change strategy based on query.

### 24. Iterative Retrieval
Multiple retrieval rounds + follow-up queries.

---

## 📊 EVALUATION — QUALITY ASSESSMENT

### 25. DeepEval
Evaluate correctness, faithfulness, contextual relevancy.

### 26. GroUSE Evaluation
Measure final answer quality across 6 foundational criteria.

---

## 🔬 EXPLAINABILITY — TRANSPARENCY

### 27. Explainable Retrieval
Clearly explain why chunks were selected.

---

## 🏗️ ADVANCED ARCHITECTURES

### 28. Agentic RAG with Contextual AI
Production-ready pipeline: document parser, SOTA reranker, grounded LLM, LMUnit testing.

### 29. Graph RAG with Milvus
Combine vector search + graph relationships (triplets).

### 30. Knowledge Graph Integration
Integrate structured data from KG.

### 31. Microsoft GraphRAG
Automatically analyze corpus → create community graph → improve multi-hop QA quality.

### 32. RAPTOR
Recursive Abstractive Processing → create multi-level summary tree.

### 33. Self-RAG
LLM decides whether to use retrieval or not → high accuracy.

### 34. Corrective RAG (CRAG)
Self-correcting retrieval system → combine Web Search when needed.

---

## 🌟 SPECIAL TECHNIQUE 

### 35. Sophisticated Controllable Agent
Advanced agent technique for complex problems:

**Pipeline:** question anonymization → planning → adaptive retrieval → multi-step reasoning → answer verification.

---

## Resources

**Full source code:** [https://github.com/NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques)

---

*Tags: #LLM #AI #RAG #Retrieval-Augmented-Generation*
