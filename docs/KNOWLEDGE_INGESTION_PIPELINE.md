# Knowledge Ingestion Pipeline Design for Cori RAG++ System

This document outlines the design of the Knowledge Ingestion Pipeline for Cori's RAG++ memory retrieval system, focusing on how financial expertise will be captured, processed, and stored in the knowledge base.

## 1. Pipeline Overview

The Knowledge Ingestion Pipeline transforms raw financial knowledge into structured, retrievable information through the following stages:

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Source  │    │  Text    │    │  Text    │    │ Embedding│    │  Storage │
│Collection│───►│Extraction│───►│Processing│───►│Generation│───►│   in DB  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                                      │                              ▲
                                      ▼                              │
                                ┌──────────┐    ┌──────────┐    ┌──────────┐
                                │  Chunk   │    │ Metadata │    │ Knowledge│
                                │Generation│───►│Enrichment│───►│Validation│
                                └──────────┘    └──────────┘    └──────────┘
```

## 2. Source Collection

### 2.1 Knowledge Source Types

The pipeline will support ingestion from multiple source types:

1. **Document Upload**
   - PDF financial documents
   - Word documents (DOCX)
   - Excel spreadsheets (XLSX)
   - PowerPoint presentations (PPTX)
   - Plain text files (TXT)

2. **Direct Input**
   - Expert explanations via UI
   - Structured knowledge entry forms
   - Q&A sessions with experts

3. **Web Resources**
   - Financial websites
   - Research papers
   - Industry reports
   - Regulatory documents

4. **Existing Models**
   - Sample Excel financial models
   - Model templates
   - Model documentation

### 2.2 Source Metadata Capture

For each source, the system will capture:

```python
{
    "source_id": "unique_source_identifier",
    "source_type": "document|direct_input|web|model",
    "title": "Source title or name",
    "author": "Source author or creator",
    "date_created": "Original creation date",
    "date_ingested": "Ingestion timestamp",
    "domain": "lbo|ma|debt|lending|general",
    "description": "Brief description of the source",
    "tags": ["tag1", "tag2"],
    "confidence": 0.9  # Source reliability score
}
```

## 3. Text Extraction

### 3.1 Document Parsing

The pipeline will use specialized parsers for each document type:

1. **PDF Extraction**
   - PyPDF2 for text extraction
   - PDF.js for layout-aware extraction
   - OCR (Tesseract) for scanned documents

2. **Office Document Extraction**
   - python-docx for Word documents
   - openpyxl for Excel spreadsheets
   - python-pptx for PowerPoint presentations

3. **Excel Model Extraction**
   - Formula extraction with openpyxl
   - Named range identification
   - Sheet structure analysis
   - Cell dependency mapping

### 3.2 Web Content Extraction

For web resources:
- BeautifulSoup for HTML parsing
- Newspaper3k for article extraction
- Selenium for dynamic content

### 3.3 Extraction Quality Control

The pipeline will implement:
- Character encoding normalization
- Layout preservation where relevant
- Table structure preservation
- Formula and equation extraction
- Image caption extraction

## 4. Text Processing

### 4.1 Cleaning Operations

The pipeline will perform:
- Whitespace normalization
- Special character handling
- Duplicate content removal
- Boilerplate text removal
- Header/footer removal

### 4.2 Financial Text Enhancement

Specialized processing for financial content:
- Formula standardization
- Number format normalization
- Financial abbreviation expansion
- Currency symbol standardization
- Date format standardization

### 4.3 Language Detection and Translation

For multi-language support:
- Language detection using langdetect
- Translation to English using OpenAI's translation capabilities
- Preservation of original language in metadata

## 5. Chunk Generation

### 5.1 Chunking Strategies

The pipeline will implement multiple chunking strategies:

1. **Fixed-Size Chunking**
   - 1000-1500 tokens per chunk for general content
   - Configurable overlap (default: 200 tokens)

2. **Semantic Chunking**
   - Section-based chunking using headings
   - Concept-based chunking using topic detection
   - Formula-preserving chunking for mathematical content

3. **Hierarchical Chunking**
   - Parent chunks for high-level concepts
   - Child chunks for detailed explanations
   - Cross-references between related chunks

### 5.2 Financial Domain-Specific Chunking

Specialized chunking for financial content:

1. **LBO Model Chunking**
   - Preserve debt sizing sections together
   - Keep exit analysis sections intact
   - Maintain returns calculation integrity

2. **M&A Analysis Chunking**
   - Keep accretion/dilution analyses together
   - Preserve synergy modeling sections
   - Maintain transaction structure integrity

3. **Debt Modeling Chunking**
   - Keep loan structure descriptions intact
   - Preserve covenant calculation sections
   - Maintain interest rate modeling integrity

4. **Private Lending Chunking**
   - Keep credit analysis frameworks together
   - Preserve risk assessment methodologies
   - Maintain covenant structure integrity

### 5.3 Chunk Quality Assurance

The pipeline will implement:
- Chunk coherence validation
- Concept integrity checking
- Cross-reference validation
- Duplicate chunk detection

## 6. Metadata Enrichment

### 6.1 Automatic Metadata Generation

The pipeline will automatically generate:

1. **Domain Classification**
   - LBO, M&A, Debt Modeling, Private Lending classification
   - Sub-domain tagging
   - Multi-domain identification

2. **Concept Type Identification**
   - Formula, process, principle, definition, example
   - Complexity level assessment
   - Prerequisite concept identification

3. **Keyword Extraction**
   - Financial term extraction
   - Key concept identification
   - Technical terminology recognition

4. **Related Concept Mapping**
   - Identification of related concepts
   - Prerequisite/dependency mapping
   - Complementary concept linking

### 6.2 Metadata Enhancement with LLMs

Using OpenAI to enhance metadata:
- Concept summarization
- Complexity assessment
- Knowledge gap identification
- Relationship mapping between concepts

### 6.3 Metadata Schema

Each chunk will be enriched with:

```python
{
    "chunk_id": "unique_chunk_identifier",
    "source_id": "original_source_id",
    "domain": "lbo|ma|debt|lending|general",
    "sub_domain": "debt_sizing|returns_analysis|etc",
    "concept_type": "formula|process|principle|definition|example",
    "complexity": "beginner|intermediate|advanced",
    "keywords": ["keyword1", "keyword2"],
    "related_concepts": ["concept1", "concept2"],
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "summary": "Brief summary of the chunk content",
    "confidence": 0.95  # System confidence in metadata accuracy
}
```

## 7. Embedding Generation

### 7.1 Embedding Model Selection

The pipeline will use:
- OpenAI's text-embedding-3-large model (default)
- Dimensionality: 3072
- Support for alternative models if needed

### 7.2 Embedding Generation Process

The process will include:
- Batch processing for efficiency
- Error handling and retry logic
- Rate limiting compliance
- Embedding validation

### 7.3 Embedding Storage

Embeddings will be stored with:
- Versioning to track embedding model changes
- Normalization for consistent similarity calculations
- Compression for storage efficiency (optional)

## 8. Knowledge Validation

### 8.1 Automated Validation

The pipeline will implement:
- Factual consistency checking
- Formula correctness validation
- Terminology consistency checking
- Cross-reference integrity validation

### 8.2 Expert Review Interface

A UI for expert validation:
- Knowledge review dashboard
- Correction submission interface
- Confidence scoring mechanism
- Relationship validation tools

### 8.3 Validation Workflow

The validation process will follow:
1. Automated checks flag potential issues
2. Experts review flagged content
3. Corrections are applied to the knowledge base
4. Validation status is updated in metadata

## 9. Storage in Vector Database

### 9.1 Chroma DB Integration

The pipeline will:
- Create appropriate collections based on domains
- Store chunks with their embeddings and metadata
- Implement efficient batch insertion
- Handle updates to existing knowledge

### 9.2 Indexing Strategy

The system will use:
- Approximate Nearest Neighbor (ANN) indexing
- Metadata-based filtering capabilities
- Hybrid search support

### 9.3 Storage Optimization

For efficient storage:
- Implement deduplication of similar chunks
- Compress embeddings where appropriate
- Archive rarely accessed knowledge

## 10. Knowledge Ingestion API

### 10.1 API Endpoints

The system will provide the following API endpoints:

```
POST /api/knowledge/upload              # Upload document files
POST /api/knowledge/direct-input        # Submit direct expert input
POST /api/knowledge/web-resource        # Ingest from web URL
POST /api/knowledge/excel-model         # Upload Excel model
GET  /api/knowledge/status/:job_id      # Check ingestion job status
GET  /api/knowledge/validation/:chunk_id # Get chunk for validation
POST /api/knowledge/validation/:chunk_id # Submit validation result
```

### 10.2 Asynchronous Processing

The API will support:
- Asynchronous job submission
- Progress tracking
- Notification on completion
- Error reporting

## 11. Implementation Considerations

### 11.1 Required Dependencies

```python
# Python dependencies for knowledge ingestion
chromadb==0.4.18
openai==1.12.0
pypdf2==3.0.1
python-docx==0.8.11
openpyxl==3.1.2
python-pptx==0.6.21
beautifulsoup4==4.12.2
newspaper3k==0.2.8
langdetect==1.0.9
numpy==1.26.0
pydantic==2.5.2
python-dotenv==1.0.0
celery==5.3.4  # For async processing
```

### 11.2 Directory Structure

```
backend/
├── knowledge_ingestion/
│   ├── __init__.py
│   ├── source_collectors/
│   │   ├── __init__.py
│   │   ├── document_collector.py
│   │   ├── direct_input_collector.py
│   │   ├── web_collector.py
│   │   └── excel_collector.py
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py
│   │   ├── office_extractor.py
│   │   ├── web_extractor.py
│   │   └── excel_extractor.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── text_cleaner.py
│   │   ├── financial_enhancer.py
│   │   └── language_processor.py
│   ├── chunkers/
│   │   ├── __init__.py
│   │   ├── fixed_size_chunker.py
│   │   ├── semantic_chunker.py
│   │   └── hierarchical_chunker.py
│   ├── metadata/
│   │   ├── __init__.py
│   │   ├── metadata_generator.py
│   │   ├── llm_enhancer.py
│   │   └── relationship_mapper.py
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── openai_embedder.py
│   │   └── embedding_manager.py
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── automated_validator.py
│   │   └── expert_review_manager.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── chroma_manager.py
│   │   └── index_optimizer.py
│   └── api/
│       ├── __init__.py
│       ├── ingestion_api.py
│       └── validation_api.py
```

## 12. Teaching Cori Financial Expertise

### 12.1 Document Upload Process

To teach Cori through document upload:

1. **Preparation**:
   - Collect high-quality financial documents covering LBO, M&A, debt modeling, and private lending
   - Organize documents by domain and complexity
   - Ensure documents contain formulas, examples, and explanations

2. **Upload Interface**:
   - Drag-and-drop interface for document upload
   - Batch upload capability
   - Domain and description tagging
   - Confidence level assignment

3. **Processing Feedback**:
   - Visual progress indicator
   - Extraction quality metrics
   - Issue flagging for manual review
   - Preview of extracted knowledge

4. **Validation**:
   - Side-by-side comparison of source and extracted knowledge
   - Correction interface for inaccuracies
   - Relationship mapping visualization
   - Approval workflow before knowledge base insertion

### 12.2 Interactive Teaching Process

To teach Cori through direct interaction:

1. **Teaching Session Interface**:
   - Topic selection (LBO, M&A, debt, lending)
   - Concept definition form
   - Formula editor with financial notation support
   - Example submission interface

2. **Guided Teaching Flow**:
   - Step-by-step concept explanation wizard
   - Prerequisite concept linking
   - Complexity level assignment
   - Related concept suggestion

3. **Knowledge Verification**:
   - Q&A testing of taught concepts
   - Paraphrasing of learned knowledge
   - Application to sample problems
   - Feedback collection on accuracy

4. **Iterative Refinement**:
   - Identification of knowledge gaps
   - Suggestion of concepts to teach next
   - Tracking of teaching progress
   - Knowledge base coverage visualization

### 12.3 Example-Based Learning Process

To teach Cori through Excel model examples:

1. **Model Upload**:
   - Excel file upload interface
   - Model type classification
   - Sheet and named range selection
   - Formula focus areas identification

2. **Annotation Interface**:
   - Cell and formula annotation tools
   - Section purpose labeling
   - Best practice flagging
   - Common pitfall marking

3. **Pattern Extraction**:
   - Automatic detection of modeling patterns
   - Formula template extraction
   - Naming convention identification
   - Structure analysis

4. **Library Creation**:
   - Categorized model technique library
   - Searchable formula repository
   - Best practice collection
   - Template gallery

### 12.4 Feedback Loop Integration

To teach Cori through ongoing feedback:

1. **Feedback Collection**:
   - Inline correction interface
   - Rating system for responses
   - Comment submission for improvements
   - Error reporting mechanism

2. **Feedback Analysis**:
   - Pattern recognition in feedback
   - Common error identification
   - Knowledge gap detection
   - Improvement prioritization

3. **Knowledge Update Process**:
   - Automated knowledge correction
   - Expert review of significant changes
   - Version control of knowledge updates
   - Before/after comparison

4. **Continuous Improvement**:
   - Performance metrics tracking
   - Feedback incorporation rate
   - Knowledge quality scoring
   - Learning curve visualization

This comprehensive knowledge ingestion pipeline design provides the foundation for teaching Cori specialized financial expertise across LBO, M&A, debt modeling, and private lending domains, with multiple teaching methods to accommodate different knowledge sources and expert interaction styles.
