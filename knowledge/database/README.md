# Database Knowledge Ingestion

This directory contains configuration files for ingesting knowledge from external databases into Vortex.

## Usage

To ingest data from a database, use the following command:

```bash
python ingest_knowledge.py --source knowledge/database --type database --config knowledge/database/your_config.json
```

## Configuration File Format

The configuration file is a JSON file with the following structure:

```json
{
    "db_type": "postgresql",
    "connection": {
        "host": "localhost",
        "port": "5432",
        "dbname": "source_db",
        "user": "db_user",
        "password": "db_password"
    },
    "query": "SELECT id, title, content, author, created_at, category FROM articles WHERE published = true",
    "content_columns": ["title", "content"],
    "metadata_columns": ["id", "author", "created_at", "category"]
}
```

### Parameters

- `db_type`: The type of database. Supported values are:
  - `postgresql`
  - `mysql`
  - `mssql`
  - `sqlite`

- `connection`: Database connection parameters:
  - For PostgreSQL, MySQL, and MSSQL:
    - `host`: Database server hostname
    - `port`: Database server port
    - `dbname`: Database name
    - `user`: Database username
    - `password`: Database password
  - For SQLite:
    - `path`: Path to the SQLite database file

- `query`: SQL query to retrieve data from the database

- `content_columns`: List of columns to include in the document content. These columns will be used to create the text that will be embedded.

- `metadata_columns`: List of columns to include as metadata for each document. These columns will be stored as metadata but not included in the embeddings.

## Sample Configuration Files

This directory includes sample configuration files for different database types:

- `sample_config.json`: PostgreSQL database example
- `mysql_config.json`: MySQL database example
- `sqlite_config.json`: SQLite database example

## Security Considerations

- Store your configuration files securely, as they contain database credentials
- Consider using environment variables for sensitive information
- Use database users with read-only permissions when possible
- Limit the query to only retrieve necessary data