#!/usr/bin/env python
"""
Knowledge Ingestion Script for Vortex AI

This script ingests knowledge from various sources (PDF, Markdown, URLs) into the Vortex knowledge base.
It processes the content, creates embeddings, and stores them in the PostgreSQL database.

Usage:
    python ingest_knowledge.py --source <source_directory> --type <content_type>

Content types:
    - pdf: PDF documents
    - markdown: Markdown files
    - url: Web URLs (from a text file with one URL per line)
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time
import re
import requests
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

try:
    import psycopg2
    from psycopg2.extras import execute_values
    import numpy as np
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.document_loaders import (
        PyPDFLoader,
        UnstructuredMarkdownLoader,
        WebBaseLoader
    )
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores.pgvector import PGVector
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"Required dependency not found: {e}")
    logger.info("Installing required dependencies...")
    os.system("pip install psycopg2-binary langchain langchain-openai pypdf unstructured python-dotenv pgvector")
    logger.info("Dependencies installed. Please run the script again.")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vortex_db")
DB_USER = os.getenv("DB_USER", "vortex")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Collection name for vector store
COLLECTION_NAME = "vortex_knowledge"

def check_database_connection() -> bool:
    """Check if the database connection is working."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

def check_vector_extension() -> bool:
    """Check if the vector extension is installed in PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking vector extension: {e}")
        return False

def get_connection_string() -> str:
    """Get the PostgreSQL connection string."""
    return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def process_pdf_files(source_dir: Path) -> List[dict]:
    """Process PDF files from the source directory."""
    logger.info(f"Processing PDF files from {source_dir}")
    documents = []
    
    pdf_files = list(source_dir.glob("**/*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {source_dir}")
        return documents
    
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading PDF: {pdf_path}")
            loader = PyPDFLoader(str(pdf_path))
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata["source"] = str(pdf_path)
                doc.metadata["type"] = "pdf"
            
            documents.extend(docs)
            logger.info(f"Loaded {len(docs)} pages from {pdf_path}")
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
    
    return documents

def process_markdown_files(source_dir: Path) -> List[dict]:
    """Process Markdown files from the source directory."""
    logger.info(f"Processing Markdown files from {source_dir}")
    documents = []
    
    md_files = list(source_dir.glob("**/*.md"))
    if not md_files:
        logger.warning(f"No Markdown files found in {source_dir}")
        return documents
    
    for md_path in md_files:
        try:
            logger.info(f"Loading Markdown: {md_path}")
            loader = UnstructuredMarkdownLoader(str(md_path))
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata["source"] = str(md_path)
                doc.metadata["type"] = "markdown"
            
            documents.extend(docs)
            logger.info(f"Loaded content from {md_path}")
        except Exception as e:
            logger.error(f"Error processing Markdown {md_path}: {e}")
    
    return documents

def process_urls(source_file: Path) -> List[dict]:
    """Process URLs from a text file."""
    logger.info(f"Processing URLs from {source_file}")
    documents = []
    
    if not source_file.exists():
        logger.warning(f"URL source file {source_file} not found")
        return documents
    
    try:
        with open(source_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            logger.warning(f"No URLs found in {source_file}")
            return documents
        
        for url in urls:
            try:
                logger.info(f"Loading URL: {url}")
                loader = WebBaseLoader(url)
                docs = loader.load()
                
                # Add metadata
                for doc in docs:
                    doc.metadata["source"] = url
                    doc.metadata["type"] = "url"
                    # Extract domain for additional metadata
                    parsed_url = urlparse(url)
                    doc.metadata["domain"] = parsed_url.netloc
                
                documents.extend(docs)
                logger.info(f"Loaded content from {url}")
                
                # Be nice to servers
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
    except Exception as e:
        logger.error(f"Error reading URL file {source_file}: {e}")
    
    return documents

def split_documents(documents: List[dict]) -> List[dict]:
    """Split documents into chunks."""
    logger.info(f"Splitting {len(documents)} documents into chunks")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    return chunks

def create_embeddings_and_store(chunks: List[dict]) -> None:
    """Create embeddings and store in the database."""
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    logger.info("Creating embeddings and storing in the database")
    
    # Initialize the embedding model
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Initialize the vector store
    connection_string = get_connection_string()
    
    try:
        # Store documents in the vector store
        PGVector.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            connection_string=connection_string,
        )
        
        logger.info(f"Successfully stored {len(chunks)} chunks in the database")
    except Exception as e:
        logger.error(f"Error storing embeddings: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge into Vortex")
    parser.add_argument("--source", required=True, help="Source directory or file")
    parser.add_argument("--type", required=True, choices=["pdf", "markdown", "url"], 
                        help="Type of content to ingest")
    
    args = parser.parse_args()
    
    source_path = Path(args.source)
    if not source_path.exists():
        logger.error(f"Source path {source_path} does not exist")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        logger.error("Failed to connect to the database. Please check your database configuration.")
        sys.exit(1)
    
    # Check vector extension
    if not check_vector_extension():
        logger.error("Vector extension is not installed in PostgreSQL. Please install it first.")
        sys.exit(1)
    
    # Process files based on type
    documents = []
    if args.type == "pdf":
        documents = process_pdf_files(source_path)
    elif args.type == "markdown":
        documents = process_markdown_files(source_path)
    elif args.type == "url":
        documents = process_urls(source_path)
    
    if not documents:
        logger.warning("No documents were processed. Exiting.")
        sys.exit(0)
    
    # Split documents into chunks
    chunks = split_documents(documents)
    
    # Create embeddings and store in the database
    create_embeddings_and_store(chunks)
    
    logger.info("Knowledge ingestion completed successfully")

if __name__ == "__main__":
    main()