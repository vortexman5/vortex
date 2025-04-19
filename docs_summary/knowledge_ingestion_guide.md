# Knowledge Ingestion Guide for Vortex

This guide provides detailed instructions for feeding external knowledge sources such as books, documentation, research papers, and other materials into Vortex to enhance its domain-specific knowledge and capabilities.

## Table of Contents

1. [Introduction](#introduction)
2. [Knowledge Ingestion Architecture](#knowledge-ingestion-architecture)
3. [Setting Up the Knowledge Database](#setting-up-the-knowledge-database)
4. [Document Processing Pipeline](#document-processing-pipeline)
5. [Ingesting Different Document Types](#ingesting-different-document-types)
6. [Knowledge Retrieval and Integration](#knowledge-retrieval-and-integration)
7. [Knowledge Maintenance and Updates](#knowledge-maintenance-and-updates)
8. [Advanced Configuration](#advanced-configuration)
9. [Troubleshooting](#troubleshooting)

## Introduction

Vortex's knowledge ingestion system allows you to enhance the AI's capabilities by feeding it domain-specific knowledge from various sources. This enables Vortex to:

- Provide more accurate and contextually relevant responses
- Understand domain-specific terminology and concepts
- Reference specific documents, books, or papers when answering questions
- Apply specialized knowledge to problem-solving tasks

The knowledge ingestion process involves:
1. Preparing your knowledge sources
2. Processing and chunking the documents
3. Generating embeddings for semantic search
4. Storing the knowledge in a vector database
5. Configuring Vortex to access and utilize this knowledge

## Knowledge Ingestion Architecture

Vortex uses a multi-stage architecture for knowledge ingestion:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Document     │     │  Document     │     │  Embedding    │     │  Vector       │
│  Collection   │────▶│  Processing   │────▶│  Generation   │────▶│  Database     │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                                          │
                                                                          ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Vortex       │◀────│  Knowledge    │◀────│  Retrieval    │◀────│  Knowledge    │
│  Response     │     │  Integration  │     │  Engine       │     │  Index        │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

## Setting Up the Knowledge Database

Before ingesting documents, you need to set up a vector database to store the knowledge. Follow these steps:

### 1. Install Required Dependencies

```bash
pip install pgvector psycopg2-binary pypdf langchain sentence-transformers
```

### 2. Set Up PostgreSQL with pgvector

If you haven't already set up PostgreSQL with the pgvector extension, follow the instructions in the [Database Setup Guide](database_setup_guide.md).

### 3. Create Knowledge Database Schema

```sql
-- Connect to your database
\c vortex_knowledge

-- Create a table for document metadata
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    author TEXT,
    publication_date DATE,
    document_type TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create a table for document chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster retrieval
CREATE INDEX ON document_chunks USING GIN (metadata jsonb_path_ops);
CREATE INDEX ON document_chunks (document_id, chunk_index);
CREATE INDEX ON documents USING GIN (tags);
```

## Document Processing Pipeline

The document processing pipeline handles the ingestion of various document types into the knowledge database.

### 1. Create a Document Processor

Create a Python script called `document_processor.py`:

```python
import os
import json
import argparse
import psycopg2
from psycopg2.extras import Json, execute_values
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import re
import logging
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, db_config: Dict[str, Any], embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the document processor.
        
        Args:
            db_config: Database configuration dictionary
            embedding_model: Name of the sentence transformer model to use
        """
        self.db_config = db_config
        self.embedding_model = SentenceTransformer(embedding_model)
        self.conn = self._connect_to_db()
    
    def _connect_to_db(self) -> psycopg2.extensions.connection:
        """Connect to the PostgreSQL database."""
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def process_document(self, file_path: str, metadata: Dict[str, Any]) -> int:
        """
        Process a document and store it in the database.
        
        Args:
            file_path: Path to the document file
            metadata: Document metadata
            
        Returns:
            document_id: ID of the inserted document
        """
        try:
            # Extract document content based on file type
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                content = self._extract_pdf_content(file_path)
            elif file_extension == '.txt':
                content = self._extract_text_content(file_path)
            elif file_extension in ['.md', '.markdown']:
                content = self._extract_text_content(file_path)
            elif file_extension in ['.html', '.htm']:
                content = self._extract_html_content(file_path)
            elif file_extension in ['.docx', '.doc']:
                content = self._extract_docx_content(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return None
            
            # Insert document metadata
            document_id = self._insert_document_metadata(metadata)
            
            # Chunk the document
            chunks = self._chunk_text(content)
            logger.info(f"Document chunked into {len(chunks)} parts")
            
            # Process and store chunks
            self._process_chunks(document_id, chunks, metadata)
            
            return document_id
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {e}")
            raise
    
    def _extract_pdf_content(self, file_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF content from {file_path}: {e}")
            raise
    
    def _extract_text_content(self, file_path: str) -> str:
        """Extract content from a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error extracting text content from {file_path}: {e}")
            raise
    
    def _extract_html_content(self, file_path: str) -> str:
        """Extract text content from an HTML file."""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.extract()
                # Get text
                text = soup.get_text()
                # Break into lines and remove leading and trailing space
                lines = (line.strip() for line in text.splitlines())
                # Break multi-headlines into a line each
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                # Drop blank lines
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text
        except ImportError:
            logger.error("BeautifulSoup4 is required for HTML processing. Install with: pip install beautifulsoup4")
            raise
        except Exception as e:
            logger.error(f"Error extracting HTML content from {file_path}: {e}")
            raise
    
    def _extract_docx_content(self, file_path: str) -> str:
        """Extract text content from a DOCX file."""
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return '\n'.join(full_text)
        except ImportError:
            logger.error("python-docx is required for DOCX processing. Install with: pip install python-docx")
            raise
        except Exception as e:
            logger.error(f"Error extracting DOCX content from {file_path}: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: The text to split
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed chunk size, save current chunk and start a new one
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                # Start new chunk with overlap from the end of the previous chunk
                if len(current_chunk) > overlap:
                    # Find the last complete sentence within the overlap
                    overlap_text = current_chunk[-overlap:]
                    sentence_end = max(overlap_text.rfind('.'), overlap_text.rfind('!'), overlap_text.rfind('?'))
                    if sentence_end != -1:
                        current_chunk = current_chunk[-(overlap-sentence_end):]
                    else:
                        current_chunk = current_chunk[-overlap:]
                else:
                    current_chunk = current_chunk
            
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
        
        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _insert_document_metadata(self, metadata: Dict[str, Any]) -> int:
        """
        Insert document metadata into the database.
        
        Args:
            metadata: Document metadata
            
        Returns:
            document_id: ID of the inserted document
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO documents (title, source, author, publication_date, document_type, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                cur.execute(query, (
                    metadata.get('title', 'Untitled'),
                    metadata.get('source', 'Unknown'),
                    metadata.get('author'),
                    metadata.get('publication_date'),
                    metadata.get('document_type', 'unknown'),
                    metadata.get('tags', [])
                ))
                
                document_id = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Inserted document metadata with ID: {document_id}")
                return document_id
                
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting document metadata: {e}")
            raise
    
    def _process_chunks(self, document_id: int, chunks: List[str], metadata: Dict[str, Any]) -> None:
        """
        Process and store document chunks.
        
        Args:
            document_id: ID of the document
            chunks: List of text chunks
            metadata: Document metadata
        """
        try:
            # Generate embeddings for all chunks
            embeddings = self.embedding_model.encode(chunks)
            
            # Prepare data for batch insertion
            chunk_data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_metadata = {
                    'document_title': metadata.get('title', 'Untitled'),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'document_type': metadata.get('document_type', 'unknown'),
                    'source': metadata.get('source', 'Unknown')
                }
                
                chunk_data.append((
                    document_id,
                    i,
                    chunk,
                    embedding.tolist(),
                    Json(chunk_metadata)
                ))
            
            # Insert chunks in batches
            with self.conn.cursor() as cur:
                query = """
                INSERT INTO document_chunks (document_id, chunk_index, content, embedding, metadata)
                VALUES %s
                """
                
                execute_values(cur, query, chunk_data, template='(%s, %s, %s, %s, %s)')
                self.conn.commit()
                
            logger.info(f"Inserted {len(chunks)} chunks for document ID: {document_id}")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error processing chunks: {e}")
            raise
    
    def search_similar(self, query: str, limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for similar content in the knowledge base.
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            
        Returns:
            List of search results
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Build the SQL query
            sql = """
            SELECT 
                dc.id, 
                dc.content, 
                dc.metadata, 
                d.title, 
                d.source,
                d.author,
                1 - (dc.embedding <=> %s) AS similarity
            FROM 
                document_chunks dc
            JOIN 
                documents d ON dc.document_id = d.id
            """
            
            params = [query_embedding]
            
            # Add filters if provided
            if filters:
                where_clauses = []
                
                if 'document_type' in filters:
                    where_clauses.append("d.document_type = %s")
                    params.append(filters['document_type'])
                
                if 'author' in filters:
                    where_clauses.append("d.author = %s")
                    params.append(filters['author'])
                
                if 'tags' in filters and filters['tags']:
                    where_clauses.append("d.tags @> %s")
                    params.append(filters['tags'])
                
                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ordering and limit
            sql += """
            ORDER BY similarity DESC
            LIMIT %s
            """
            params.append(limit)
            
            # Execute the query
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                results = cur.fetchall()
            
            # Format the results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'id': row[0],
                    'content': row[1],
                    'metadata': row[2],
                    'document_title': row[3],
                    'source': row[4],
                    'author': row[5],
                    'similarity': row[6]
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar content: {e}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Process documents for Vortex knowledge base')
    parser.add_argument('--file', type=str, help='Path to the document file')
    parser.add_argument('--dir', type=str, help='Path to directory containing documents')
    parser.add_argument('--metadata', type=str, help='Path to JSON file with document metadata')
    parser.add_argument('--db-config', type=str, required=True, help='Path to database configuration JSON file')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--limit', type=int, default=5, help='Maximum number of search results')
    
    args = parser.parse_args()
    
    # Load database configuration
    with open(args.db_config, 'r') as f:
        db_config = json.load(f)
    
    processor = DocumentProcessor(db_config)
    
    try:
        if args.search:
            # Search mode
            results = processor.search_similar(args.search, args.limit)
            print(f"Search results for '{args.search}':")
            for i, result in enumerate(results):
                print(f"\n--- Result {i+1} (Similarity: {result['similarity']:.4f}) ---")
                print(f"Document: {result['document_title']}")
                print(f"Source: {result['source']}")
                if result['author']:
                    print(f"Author: {result['author']}")
                print(f"\nContent:\n{result['content'][:500]}...")
        
        elif args.file:
            # Process a single file
            if not args.metadata:
                logger.error("Metadata file is required when processing a document")
                return
            
            # Load metadata
            with open(args.metadata, 'r') as f:
                metadata = json.load(f)
            
            document_id = processor.process_document(args.file, metadata)
            print(f"Processed document with ID: {document_id}")
        
        elif args.dir:
            # Process all files in a directory
            if not args.metadata:
                logger.error("Metadata file is required when processing documents")
                return
            
            # Load metadata
            with open(args.metadata, 'r') as f:
                metadata_list = json.load(f)
            
            # Check if metadata is a list or a single item
            if not isinstance(metadata_list, list):
                metadata_list = [metadata_list]
            
            # Create a mapping of filenames to metadata
            metadata_map = {m.get('filename', ''): m for m in metadata_list}
            
            # Process each file in the directory
            processed_count = 0
            for filename in os.listdir(args.dir):
                file_path = os.path.join(args.dir, filename)
                if os.path.isfile(file_path):
                    # Get metadata for this file
                    if filename in metadata_map:
                        file_metadata = metadata_map[filename]
                        document_id = processor.process_document(file_path, file_metadata)
                        if document_id:
                            processed_count += 1
                            print(f"Processed {filename} with ID: {document_id}")
                    else:
                        logger.warning(f"No metadata found for {filename}, skipping")
            
            print(f"Processed {processed_count} documents")
        
        else:
            logger.error("Either --file, --dir, or --search must be specified")
    
    finally:
        processor.close()

if __name__ == "__main__":
    main()
```

### 2. Create a Database Configuration File

Create a file named `db_config.json`:

```json
{
    "host": "localhost",
    "port": 5432,
    "database": "vortex_knowledge",
    "user": "vortex",
    "password": "your_secure_password"
}
```

### 3. Create a Metadata Template

Create a file named `metadata_template.json`:

```json
{
    "title": "Document Title",
    "source": "Source URL or Book Title",
    "author": "Author Name",
    "publication_date": "2023-01-01",
    "document_type": "book",
    "tags": ["tag1", "tag2"],
    "filename": "document.pdf"
}
```

## Ingesting Different Document Types

### Books and PDFs

1. Prepare your PDF files in a directory
2. Create a metadata JSON file for each book:

```json
{
    "title": "Advanced Machine Learning Techniques",
    "source": "Advanced ML Techniques, 3rd Edition",
    "author": "Jane Smith",
    "publication_date": "2022-05-15",
    "document_type": "book",
    "tags": ["machine learning", "artificial intelligence", "data science"],
    "filename": "advanced_ml_techniques.pdf"
}
```

3. Run the document processor:

```bash
python document_processor.py --file /path/to/advanced_ml_techniques.pdf --metadata /path/to/book_metadata.json --db-config db_config.json
```

### Technical Documentation

1. Organize your documentation files (HTML, Markdown, etc.)
2. Create a metadata JSON file:

```json
[
    {
        "title": "API Reference Guide",
        "source": "Company Internal Documentation",
        "author": "Development Team",
        "publication_date": "2023-02-10",
        "document_type": "documentation",
        "tags": ["api", "reference", "development"],
        "filename": "api_reference.md"
    },
    {
        "title": "System Architecture Overview",
        "source": "Company Internal Documentation",
        "author": "Architecture Team",
        "publication_date": "2023-01-20",
        "document_type": "documentation",
        "tags": ["architecture", "system design", "infrastructure"],
        "filename": "system_architecture.html"
    }
]
```

3. Process all documentation files in a directory:

```bash
python document_processor.py --dir /path/to/documentation --metadata /path/to/docs_metadata.json --db-config db_config.json
```

### Research Papers

1. Collect research papers in PDF format
2. Create metadata for the papers:

```json
[
    {
        "title": "Attention Is All You Need",
        "source": "Advances in Neural Information Processing Systems",
        "author": "Vaswani et al.",
        "publication_date": "2017-12-05",
        "document_type": "research_paper",
        "tags": ["transformers", "attention", "nlp"],
        "filename": "attention_is_all_you_need.pdf"
    }
]
```

3. Process the papers:

```bash
python document_processor.py --dir /path/to/papers --metadata /path/to/papers_metadata.json --db-config db_config.json
```

## Knowledge Retrieval and Integration

### 1. Testing Knowledge Retrieval

You can test if your knowledge has been properly ingested by searching for relevant content:

```bash
python document_processor.py --search "How do transformer models work?" --limit 5 --db-config db_config.json
```

### 2. Integrating with Vortex

To integrate the knowledge database with Vortex, you need to configure Vortex to use the vector database for knowledge retrieval.

Create or modify your Vortex configuration file:

```toml
[database]
enable_database_storage = true

[database.vector]
type = "postgresql"
host = "localhost"
port = 5432
user = "vortex"
password = "your_secure_password"
database = "vortex_knowledge"
table_name = "document_chunks"
vector_dimension = 1536

[memory]
type = "database"
persistence = true
use_vector_db = true
vector_db_config = "database.vector"

[knowledge]
enable_external_knowledge = true
knowledge_sources = ["database.vector"]
max_knowledge_results = 5
knowledge_similarity_threshold = 0.7
```

### 3. Creating a Knowledge Retrieval Microagent

To make the most of your ingested knowledge, create a specialized microagent for knowledge retrieval:

```python
# knowledge_microagent.py
from openhands.microagents.base import BaseMicroagent
import psycopg2
import json
from sentence_transformers import SentenceTransformer

class KnowledgeRetrievalMicroagent(BaseMicroagent):
    """A microagent for retrieving knowledge from the vector database."""
    
    def __init__(self):
        super().__init__(
            name="KnowledgeRetrievalMicroagent",
            description="Retrieves relevant knowledge from the knowledge database",
            triggers=["knowledge", "information", "reference", "book", "paper", "documentation"]
        )
        
        # Load configuration
        with open('/path/to/db_config.json', 'r') as f:
            self.db_config = json.load(f)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def get_prompt_extension(self, context):
        """Retrieve relevant knowledge based on the user's query."""
        query = context.get("user_message", "")
        
        if not query:
            return ""
        
        # Retrieve relevant knowledge
        knowledge = self._retrieve_knowledge(query)
        
        if not knowledge:
            return ""
        
        # Format the knowledge as a prompt extension
        prompt_extension = "# Relevant Knowledge\n\n"
        
        for i, item in enumerate(knowledge):
            prompt_extension += f"## Source {i+1}: {item['document_title']}\n"
            if item['author']:
                prompt_extension += f"Author: {item['author']}\n"
            prompt_extension += f"Source: {item['source']}\n\n"
            prompt_extension += f"{item['content']}\n\n"
        
        return prompt_extension
    
    def _retrieve_knowledge(self, query, limit=3):
        """Retrieve relevant knowledge from the database."""
        try:
            # Connect to the database
            conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search for similar content
            with conn.cursor() as cur:
                sql = """
                SELECT 
                    dc.id, 
                    dc.content, 
                    dc.metadata, 
                    d.title, 
                    d.source,
                    d.author,
                    1 - (dc.embedding <=> %s) AS similarity
                FROM 
                    document_chunks dc
                JOIN 
                    documents d ON dc.document_id = d.id
                WHERE
                    1 - (dc.embedding <=> %s) > 0.7
                ORDER BY similarity DESC
                LIMIT %s
                """
                
                cur.execute(sql, [query_embedding, query_embedding, limit])
                results = cur.fetchall()
            
            # Format the results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    'id': row[0],
                    'content': row[1],
                    'metadata': row[2],
                    'document_title': row[3],
                    'source': row[4],
                    'author': row[5],
                    'similarity': row[6]
                })
            
            conn.close()
            return formatted_results
            
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return []
```

Register the microagent in Vortex:

```python
# In openhands/microagents/__init__.py
from openhands.microagents.registry import register_microagent
from path.to.knowledge_microagent import KnowledgeRetrievalMicroagent

register_microagent(KnowledgeRetrievalMicroagent())
```

## Knowledge Maintenance and Updates

### 1. Updating Existing Knowledge

To update existing knowledge:

1. Identify the document to update:

```sql
SELECT id, title, source FROM documents WHERE title LIKE '%Machine Learning%';
```

2. Delete the existing document and its chunks:

```sql
DELETE FROM documents WHERE id = 123;
```

3. Process the updated document:

```bash
python document_processor.py --file /path/to/updated_document.pdf --metadata /path/to/updated_metadata.json --db-config db_config.json
```

### 2. Batch Processing New Knowledge

Create a script for batch processing new documents:

```python
# batch_process.py
import os
import json
import argparse
from document_processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description='Batch process documents for Vortex knowledge base')
    parser.add_argument('--dir', type=str, required=True, help='Directory containing documents')
    parser.add_argument('--metadata-dir', type=str, required=True, help='Directory containing metadata JSON files')
    parser.add_argument('--db-config', type=str, required=True, help='Path to database configuration JSON file')
    
    args = parser.parse_args()
    
    # Load database configuration
    with open(args.db_config, 'r') as f:
        db_config = json.load(f)
    
    processor = DocumentProcessor(db_config)
    
    try:
        # Process each file in the directory
        processed_count = 0
        for filename in os.listdir(args.dir):
            file_path = os.path.join(args.dir, filename)
            if os.path.isfile(file_path):
                # Look for corresponding metadata file
                metadata_file = os.path.join(args.metadata_dir, f"{os.path.splitext(filename)[0]}.json")
                
                if os.path.exists(metadata_file):
                    # Load metadata
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    
                    # Add filename to metadata if not present
                    if 'filename' not in metadata:
                        metadata['filename'] = filename
                    
                    # Process the document
                    document_id = processor.process_document(file_path, metadata)
                    if document_id:
                        processed_count += 1
                        print(f"Processed {filename} with ID: {document_id}")
                else:
                    print(f"No metadata found for {filename}, skipping")
        
        print(f"Processed {processed_count} documents")
    
    finally:
        processor.close()

if __name__ == "__main__":
    main()
```

Run the batch processing script:

```bash
python batch_process.py --dir /path/to/new_documents --metadata-dir /path/to/metadata_files --db-config db_config.json
```

### 3. Scheduled Knowledge Updates

Set up a cron job to regularly check for and process new documents:

```bash
# Create a shell script for the update process
cat > update_knowledge.sh << 'EOF'
#!/bin/bash

# Configuration
DOCUMENTS_DIR="/path/to/documents"
PROCESSED_DIR="/path/to/processed_documents"
METADATA_DIR="/path/to/metadata"
DB_CONFIG="/path/to/db_config.json"
LOG_FILE="/path/to/knowledge_update.log"

# Log start time
echo "Starting knowledge update at $(date)" >> $LOG_FILE

# Check for new documents
for file in "$DOCUMENTS_DIR"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        metadata_file="$METADATA_DIR/${filename%.*}.json"
        
        # Check if metadata exists
        if [ -f "$metadata_file" ]; then
            echo "Processing $filename" >> $LOG_FILE
            
            # Process the document
            python /path/to/document_processor.py --file "$file" --metadata "$metadata_file" --db-config "$DB_CONFIG" >> $LOG_FILE 2>&1
            
            # Move to processed directory if successful
            if [ $? -eq 0 ]; then
                mv "$file" "$PROCESSED_DIR/"
                echo "Successfully processed $filename" >> $LOG_FILE
            else
                echo "Failed to process $filename" >> $LOG_FILE
            fi
        else
            echo "No metadata found for $filename" >> $LOG_FILE
        fi
    fi
done

echo "Finished knowledge update at $(date)" >> $LOG_FILE
EOF

# Make the script executable
chmod +x update_knowledge.sh

# Add to crontab to run daily at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/update_knowledge.sh") | crontab -
```

## Advanced Configuration

### 1. Custom Embedding Models

You can use different embedding models for different types of knowledge:

```python
# In document_processor.py, modify the __init__ method:

def __init__(self, db_config, embedding_models=None):
    self.db_config = db_config
    
    # Default embedding model
    self.default_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Specialized embedding models for different document types
    self.embedding_models = embedding_models or {
        "book": SentenceTransformer("all-mpnet-base-v2"),  # More powerful model for books
        "research_paper": SentenceTransformer("allenai/specter"),  # Specialized for research papers
        "code": SentenceTransformer("flax-sentence-embeddings/st-codesearch-distilroberta-base")  # For code documentation
    }

# Then modify the _process_chunks method to use the appropriate model:

def _process_chunks(self, document_id, chunks, metadata):
    # Select the appropriate embedding model based on document type
    document_type = metadata.get('document_type', 'unknown')
    if document_type in self.embedding_models:
        embedding_model = self.embedding_models[document_type]
    else:
        embedding_model = self.default_embedding_model
    
    # Generate embeddings
    embeddings = embedding_model.encode(chunks)
    
    # Rest of the method remains the same...
```

### 2. Knowledge Weighting and Prioritization

You can implement a system to weight knowledge sources differently:

```python
# In the KnowledgeRetrievalMicroagent class:

def _retrieve_knowledge(self, query, limit=3):
    # ... existing code ...
    
    # Add weighting based on document type and recency
    with conn.cursor() as cur:
        sql = """
        SELECT 
            dc.id, 
            dc.content, 
            dc.metadata, 
            d.title, 
            d.source,
            d.author,
            CASE
                WHEN d.document_type = 'research_paper' THEN 1.2 * (1 - (dc.embedding <=> %s))
                WHEN d.document_type = 'book' THEN 1.1 * (1 - (dc.embedding <=> %s))
                WHEN d.publication_date > '2022-01-01' THEN 1.15 * (1 - (dc.embedding <=> %s))
                ELSE 1 - (dc.embedding <=> %s)
            END AS weighted_similarity
        FROM 
            document_chunks dc
        JOIN 
            documents d ON dc.document_id = d.id
        WHERE
            1 - (dc.embedding <=> %s) > 0.7
        ORDER BY weighted_similarity DESC
        LIMIT %s
        """
        
        cur.execute(sql, [query_embedding, query_embedding, query_embedding, query_embedding, query_embedding, limit])
        # ... rest of the method ...
```

### 3. Knowledge Fusion

Implement a system to combine knowledge from multiple sources:

```python
# In the KnowledgeRetrievalMicroagent class:

def get_prompt_extension(self, context):
    query = context.get("user_message", "")
    
    if not query:
        return ""
    
    # Retrieve relevant knowledge
    knowledge = self._retrieve_knowledge(query)
    
    if not knowledge:
        return ""
    
    # Group knowledge by topic
    topics = self._cluster_by_topic(knowledge)
    
    # Format the knowledge as a prompt extension
    prompt_extension = "# Relevant Knowledge\n\n"
    
    for topic, items in topics.items():
        prompt_extension += f"## Topic: {topic}\n\n"
        
        # Synthesize information from multiple sources
        synthesis = self._synthesize_knowledge(items)
        prompt_extension += f"{synthesis}\n\n"
        
        # Add individual sources
        prompt_extension += "### Sources:\n"
        for item in items:
            prompt_extension += f"- {item['document_title']} by {item['author'] or 'Unknown'} ({item['source']})\n"
        
        prompt_extension += "\n"
    
    return prompt_extension

def _cluster_by_topic(self, knowledge_items):
    # Implement clustering logic to group related knowledge items
    # This could use embedding similarity, topic modeling, etc.
    # For simplicity, this example just puts everything in one topic
    return {"General Information": knowledge_items}

def _synthesize_knowledge(self, items):
    # Combine information from multiple sources
    combined_text = "\n\n".join([item['content'] for item in items])
    
    # Use LLM to synthesize the information
    synthesis_prompt = f"""
    Synthesize the following information into a coherent summary:
    
    {combined_text}
    
    Provide a concise, well-organized summary that combines the key points from all sources.
    """
    
    # This would call your LLM service
    # synthesis = llm_client.generate(synthesis_prompt)
    
    # For now, just return a placeholder
    synthesis = "Synthesized information would appear here."
    
    return synthesis
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues

**Problem**: Unable to connect to the PostgreSQL database.

**Solution**:
- Verify that PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in `db_config.json`
- Ensure the database and user exist: `sudo -u postgres psql -c "\du"`
- Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-14-main.log`

#### 2. Embedding Generation Errors

**Problem**: Errors when generating embeddings.

**Solution**:
- Ensure you have enough RAM for the embedding model
- Try a smaller model like "all-MiniLM-L6-v2" instead of larger models
- Process documents in smaller batches
- Check for encoding issues in your documents

#### 3. Document Processing Failures

**Problem**: Document processing fails for certain file types.

**Solution**:
- Ensure you have the necessary dependencies installed:
  - For PDF: `pip install pypdf`
  - For DOCX: `pip install python-docx`
  - For HTML: `pip install beautifulsoup4`
- Check file encoding and convert if necessary: `iconv -f ISO-8859-1 -t UTF-8 input.txt > output.txt`
- For large files, try increasing chunk size or processing in parts

#### 4. Knowledge Not Being Retrieved

**Problem**: Vortex isn't using the ingested knowledge.

**Solution**:
- Verify the knowledge is in the database: `SELECT COUNT(*) FROM document_chunks;`
- Check the similarity threshold in your configuration (try lowering it)
- Ensure the microagent is properly registered
- Test direct retrieval using the search function in `document_processor.py`
- Check that your query is relevant to the ingested knowledge

## Conclusion

This guide has provided detailed instructions for feeding external knowledge sources into Vortex. By following these steps, you can enhance Vortex's capabilities with domain-specific knowledge from books, documentation, research papers, and other sources.

The knowledge ingestion system allows Vortex to:
- Access and reference specific information from your documents
- Provide more accurate and contextually relevant responses
- Apply specialized domain knowledge to problem-solving tasks
- Cite sources when providing information

Remember to regularly update your knowledge base with new information to keep Vortex's knowledge current and comprehensive.