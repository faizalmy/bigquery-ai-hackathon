# Database Schema Definitions - BigQuery AI Legal Document Intelligence Platform

## 📋 **Document Overview**

**Purpose**: Complete BigQuery database schema definitions for the Legal Document Intelligence Platform
**Scope**: All data stores, tables, indexes, and relationships
**Standard**: BigQuery SQL DDL specifications

---

## 🏗️ **Database Architecture Overview**

### **Dataset Structure**
```
legal_ai_platform/
├── raw_data/           # Raw document storage
├── processed_data/     # Processed document storage
├── embeddings/         # Vector embeddings storage
├── results/           # Analysis results storage
├── metadata/          # System metadata storage
└── batch_processing/  # Batch job management
```

---

## 📊 **Data Store D1: Document Input Store**

### **Table: legal_documents**

```sql
-- Raw legal documents storage
CREATE TABLE `legal_ai_platform.raw_data.legal_documents` (
  document_id STRING NOT NULL,
  document_content TEXT NOT NULL,
  document_metadata JSON,
  document_type STRING,
  file_format STRING,
  file_size INTEGER,
  processing_status STRING DEFAULT 'pending',
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  created_by STRING,
  source_system STRING
)
PARTITION BY DATE(created_timestamp)
CLUSTER BY document_type, processing_status;

-- Indexes for performance
CREATE INDEX idx_legal_documents_status
ON `legal_ai_platform.raw_data.legal_documents`(processing_status);

CREATE INDEX idx_legal_documents_type
ON `legal_ai_platform.raw_data.legal_documents`(document_type);
```

### **Table: document_processing_log**

```sql
-- Document processing audit log
CREATE TABLE `legal_ai_platform.raw_data.document_processing_log` (
  log_id STRING NOT NULL,
  document_id STRING NOT NULL,
  processing_stage STRING NOT NULL,
  processing_status STRING NOT NULL,
  processing_message TEXT,
  processing_duration INTEGER,
  error_details JSON,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_timestamp)
CLUSTER BY document_id, processing_stage;
```

---

## 📊 **Data Store D2: Results Storage**

### **Table: analysis_results**

```sql
-- AI analysis results storage
CREATE TABLE `legal_ai_platform.results.analysis_results` (
  result_id STRING NOT NULL,
  document_id STRING NOT NULL,
  ai_summary TEXT,
  extracted_data JSON,
  urgency_flag BOOLEAN,
  predicted_outcome STRING,
  confidence_scores JSON,
  analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  processing_duration INTEGER,
  ai_model_version STRING,
  analysis_metadata JSON
)
PARTITION BY DATE(analysis_timestamp)
CLUSTER BY document_id, ai_model_version;

-- Indexes for performance
CREATE INDEX idx_analysis_results_document
ON `legal_ai_platform.results.analysis_results`(document_id);

CREATE INDEX idx_analysis_results_urgency
ON `legal_ai_platform.results.analysis_results`(urgency_flag);
```

### **Table: similarity_results**

```sql
-- Vector similarity search results
CREATE TABLE `legal_ai_platform.results.similarity_results` (
  similarity_id STRING NOT NULL,
  query_document_id STRING NOT NULL,
  similar_document_id STRING NOT NULL,
  similarity_score FLOAT64 NOT NULL,
  similarity_metadata JSON,
  search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  search_parameters JSON
)
PARTITION BY DATE(search_timestamp)
CLUSTER BY query_document_id, similarity_score;

-- Indexes for performance
CREATE INDEX idx_similarity_results_query
ON `legal_ai_platform.results.similarity_results`(query_document_id);

CREATE INDEX idx_similarity_results_score
ON `legal_ai_platform.results.similarity_results`(similarity_score);
```

---

## 📊 **Data Store D3: Vector Embeddings Store**

### **Table: document_embeddings**

```sql
-- Document embeddings storage
CREATE TABLE `legal_ai_platform.embeddings.document_embeddings` (
  embedding_id STRING NOT NULL,
  document_id STRING NOT NULL,
  embedding_vector ARRAY<FLOAT64> NOT NULL,
  embedding_model STRING DEFAULT 'text-embedding-preview-0409',
  embedding_dimension INTEGER DEFAULT 1024,
  embedding_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  vector_index_id STRING,
  similarity_metadata JSON,
  embedding_quality_score FLOAT64
)
PARTITION BY DATE(embedding_timestamp)
CLUSTER BY embedding_model, vector_index_id;

-- Indexes for performance
CREATE INDEX idx_document_embeddings_document
ON `legal_ai_platform.embeddings.document_embeddings`(document_id);

CREATE INDEX idx_document_embeddings_model
ON `legal_ai_platform.embeddings.document_embeddings`(embedding_model);
```

### **Table: vector_indexes**

```sql
-- Vector index metadata
CREATE TABLE `legal_ai_platform.embeddings.vector_indexes` (
  index_id STRING NOT NULL,
  index_name STRING NOT NULL,
  index_type STRING NOT NULL,
  embedding_model STRING NOT NULL,
  index_parameters JSON,
  index_status STRING DEFAULT 'active',
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  index_statistics JSON,
  performance_metrics JSON
)
PARTITION BY DATE(created_timestamp)
CLUSTER BY index_type, index_status;
```

---

## 📊 **Data Store D4: AI Model Metadata**

### **Table: ai_model_metadata**

```sql
-- AI model metadata and performance tracking
CREATE TABLE `legal_ai_platform.metadata.ai_model_metadata` (
  model_id STRING NOT NULL,
  model_name STRING NOT NULL,
  model_version STRING NOT NULL,
  model_type STRING NOT NULL,
  model_status STRING DEFAULT 'active',
  performance_metrics JSON,
  configuration_parameters JSON,
  deployment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  accuracy_history JSON,
  model_description TEXT,
  training_data_info JSON
)
PARTITION BY DATE(deployment_timestamp)
CLUSTER BY model_name, model_status;

-- Indexes for performance
CREATE INDEX idx_ai_model_metadata_name
ON `legal_ai_platform.metadata.ai_model_metadata`(model_name);

CREATE INDEX idx_ai_model_metadata_status
ON `legal_ai_platform.metadata.ai_model_metadata`(model_status);
```

### **Table: model_performance_log**

```sql
-- Model performance monitoring log
CREATE TABLE `legal_ai_platform.metadata.model_performance_log` (
  log_id STRING NOT NULL,
  model_id STRING NOT NULL,
  performance_metrics JSON,
  accuracy_score FLOAT64,
  response_time INTEGER,
  resource_usage JSON,
  log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  test_dataset_info JSON
)
PARTITION BY DATE(log_timestamp)
CLUSTER BY model_id, log_timestamp;
```

---

## 📊 **Data Store D5: Batch Processing Queue**

### **Table: batch_processing_queue**

```sql
-- Batch processing job management
CREATE TABLE `legal_ai_platform.batch_processing.batch_processing_queue` (
  batch_id STRING NOT NULL,
  batch_status STRING DEFAULT 'pending',
  document_count INTEGER NOT NULL,
  processing_start_time TIMESTAMP,
  processing_end_time TIMESTAMP,
  batch_results JSON,
  error_logs JSON,
  priority_level INTEGER DEFAULT 5,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  created_by STRING,
  batch_metadata JSON
)
PARTITION BY DATE(created_timestamp)
CLUSTER BY batch_status, priority_level;

-- Indexes for performance
CREATE INDEX idx_batch_processing_status
ON `legal_ai_platform.batch_processing.batch_processing_queue`(batch_status);

CREATE INDEX idx_batch_processing_priority
ON `legal_ai_platform.batch_processing.batch_processing_queue`(priority_level);
```

### **Table: batch_document_mapping**

```sql
-- Mapping between batches and documents
CREATE TABLE `legal_ai_platform.batch_processing.batch_document_mapping` (
  mapping_id STRING NOT NULL,
  batch_id STRING NOT NULL,
  document_id STRING NOT NULL,
  processing_order INTEGER,
  processing_status STRING DEFAULT 'pending',
  processing_result JSON,
  error_details JSON,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_timestamp)
CLUSTER BY batch_id, processing_status;

-- Indexes for performance
CREATE INDEX idx_batch_document_mapping_batch
ON `legal_ai_platform.batch_processing.batch_document_mapping`(batch_id);

CREATE INDEX idx_batch_document_mapping_document
ON `legal_ai_platform.batch_processing.batch_document_mapping`(document_id);
```

---

## 🔗 **Foreign Key Relationships**

### **Primary Relationships**

```sql
-- Document to Results relationship
ALTER TABLE `legal_ai_platform.results.analysis_results`
ADD CONSTRAINT fk_analysis_results_document
FOREIGN KEY (document_id)
REFERENCES `legal_ai_platform.raw_data.legal_documents`(document_id);

-- Document to Embeddings relationship
ALTER TABLE `legal_ai_platform.embeddings.document_embeddings`
ADD CONSTRAINT fk_document_embeddings_document
FOREIGN KEY (document_id)
REFERENCES `legal_ai_platform.raw_data.legal_documents`(document_id);

-- Embeddings to Vector Index relationship
ALTER TABLE `legal_ai_platform.embeddings.document_embeddings`
ADD CONSTRAINT fk_document_embeddings_index
FOREIGN KEY (vector_index_id)
REFERENCES `legal_ai_platform.embeddings.vector_indexes`(index_id);

-- Model to Performance Log relationship
ALTER TABLE `legal_ai_platform.metadata.model_performance_log`
ADD CONSTRAINT fk_model_performance_log_model
FOREIGN KEY (model_id)
REFERENCES `legal_ai_platform.metadata.ai_model_metadata`(model_id);

-- Batch to Document Mapping relationship
ALTER TABLE `legal_ai_platform.batch_processing.batch_document_mapping`
ADD CONSTRAINT fk_batch_document_mapping_batch
FOREIGN KEY (batch_id)
REFERENCES `legal_ai_platform.batch_processing.batch_processing_queue`(batch_id);

ALTER TABLE `legal_ai_platform.batch_processing.batch_document_mapping`
ADD CONSTRAINT fk_batch_document_mapping_document
FOREIGN KEY (document_id)
REFERENCES `legal_ai_platform.raw_data.legal_documents`(document_id);
```

---

## 📈 **Performance Optimization**

### **Partitioning Strategy**

```sql
-- All tables partitioned by timestamp for optimal query performance
-- Partitioning by date allows for:
-- 1. Efficient time-based queries
-- 2. Automatic partition pruning
-- 3. Cost optimization through partition elimination
-- 4. Easy data lifecycle management
```

### **Clustering Strategy**

```sql
-- Clustering by frequently queried columns:
-- 1. document_type, processing_status for legal_documents
-- 2. document_id, ai_model_version for analysis_results
-- 3. query_document_id, similarity_score for similarity_results
-- 4. embedding_model, vector_index_id for document_embeddings
-- 5. model_name, model_status for ai_model_metadata
-- 6. batch_status, priority_level for batch_processing_queue
```

### **Index Strategy**

```sql
-- Strategic indexes for:
-- 1. Primary key lookups
-- 2. Foreign key joins
-- 3. Filter conditions
-- 4. Order by clauses
-- 5. Range queries
```

---

## 🔒 **Security and Access Control**

### **Row-Level Security**

```sql
-- Example: Restrict access based on user roles
CREATE ROW ACCESS POLICY legal_documents_access
ON `legal_ai_platform.raw_data.legal_documents`
GRANT TO ('legal_analyst@company.com', 'legal_manager@company.com')
FILTER USING (created_by = SESSION_USER());

-- Example: Restrict access to sensitive results
CREATE ROW ACCESS POLICY analysis_results_access
ON `legal_ai_platform.results.analysis_results`
GRANT TO ('legal_analyst@company.com', 'legal_manager@company.com')
FILTER USING (document_id IN (
  SELECT document_id
  FROM `legal_ai_platform.raw_data.legal_documents`
  WHERE created_by = SESSION_USER()
));
```

### **Column-Level Security**

```sql
-- Example: Mask sensitive data for certain roles
CREATE COLUMN ACCESS POLICY mask_sensitive_data
ON `legal_ai_platform.raw_data.legal_documents`(document_content)
GRANT TO ('legal_analyst@company.com')
FILTER USING (TRUE)
REPLACE WITH ('[SENSITIVE DATA MASKED]');
```

---

## 📊 **Data Lifecycle Management**

### **Data Retention Policies**

```sql
-- Example: Automatic deletion of old processing logs
CREATE OR REPLACE TABLE `legal_ai_platform.raw_data.document_processing_log`
PARTITION BY DATE(created_timestamp)
OPTIONS (
  partition_expiration_days = 90,
  require_partition_filter = true
);

-- Example: Automatic deletion of old performance logs
CREATE OR REPLACE TABLE `legal_ai_platform.metadata.model_performance_log`
PARTITION BY DATE(log_timestamp)
OPTIONS (
  partition_expiration_days = 365,
  require_partition_filter = true
);
```

### **Data Archival Strategy**

```sql
-- Example: Archive old analysis results
CREATE OR REPLACE TABLE `legal_ai_platform.results.analysis_results_archive`
PARTITION BY DATE(analysis_timestamp)
OPTIONS (
  partition_expiration_days = 2555, -- 7 years
  require_partition_filter = true
);
```

---

## 🔄 **Data Validation and Constraints**

### **Check Constraints**

```sql
-- Example: Validate document types
ALTER TABLE `legal_ai_platform.raw_data.legal_documents`
ADD CONSTRAINT chk_document_type
CHECK (document_type IN ('contract', 'case_file', 'legal_brief', 'statute', 'other'));

-- Example: Validate processing status
ALTER TABLE `legal_ai_platform.raw_data.legal_documents`
ADD CONSTRAINT chk_processing_status
CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed', 'archived'));

-- Example: Validate similarity scores
ALTER TABLE `legal_ai_platform.results.similarity_results`
ADD CONSTRAINT chk_similarity_score
CHECK (similarity_score >= 0.0 AND similarity_score <= 1.0);

-- Example: Validate priority levels
ALTER TABLE `legal_ai_platform.batch_processing.batch_processing_queue`
ADD CONSTRAINT chk_priority_level
CHECK (priority_level >= 1 AND priority_level <= 10);
```

---

## 📋 **Schema Validation Summary**

### **Completeness Check**

**Table Coverage:**
- ✅ Document Input Store (2 tables)
- ✅ Results Storage (2 tables)
- ✅ Vector Embeddings Store (2 tables)
- ✅ AI Model Metadata (2 tables)
- ✅ Batch Processing Queue (2 tables)

**Relationship Coverage:**
- ✅ Primary-Foreign Key relationships
- ✅ Referential integrity constraints
- ✅ Data validation constraints
- ✅ Security and access controls

**Performance Optimization:**
- ✅ Partitioning strategy
- ✅ Clustering strategy
- ✅ Index strategy
- ✅ Query optimization

**Data Management:**
- ✅ Data lifecycle management
- ✅ Data retention policies
- ✅ Data archival strategy
- ✅ Security and compliance

---

*This document provides complete BigQuery database schema definitions for the Legal Document Intelligence Platform, ensuring optimal performance, security, and maintainability.*
