# Comprehensive Database Setup Guide for Vortex

This guide provides detailed instructions for setting up and configuring databases for knowledge storage and other critical components in the Vortex framework. It covers both local and remote deployment scenarios, database optimization, and integration with the Vortex memory system.

## Table of Contents

1. [Introduction to Vortex Database Architecture](#introduction-to-vortex-database-architecture)
2. [Local Database Setup](#local-database-setup)
3. [Remote Database Setup](#remote-database-setup)
4. [Vector Database for Knowledge Storage](#vector-database-for-knowledge-storage)
5. [Document Database for Unstructured Data](#document-database-for-unstructured-data)
6. [Relational Database for Structured Data](#relational-database-for-structured-data)
7. [Database Integration with Memory System](#database-integration-with-memory-system)
8. [Backup and Recovery Strategies](#backup-and-recovery-strategies)
9. [Performance Optimization](#performance-optimization)
10. [Security Best Practices](#security-best-practices)

## Introduction to Vortex Database Architecture

Vortex uses a multi-database architecture to efficiently store and retrieve different types of data:

1. **Vector Database**: For semantic search and knowledge retrieval
2. **Document Database**: For storing unstructured data, conversations, and agent states
3. **Relational Database**: For structured data, user information, and system configuration

This architecture allows Vortex to handle diverse data types while maintaining high performance and scalability.

## Local Database Setup

### Prerequisites

For local development and testing, you'll need:

```bash
# Install database dependencies
sudo apt update
sudo apt install -y postgresql postgresql-contrib redis-server
pip install pgvector pymongo redis sqlalchemy
```

### Setting Up PostgreSQL with pgvector Extension

PostgreSQL with the pgvector extension serves as an excellent local vector database:

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE USER vortex WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE vortex_knowledge;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vortex_knowledge TO vortex;"

# Install pgvector extension
sudo apt install -y postgresql-server-dev-14 build-essential git
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
cd ..

# Enable pgvector extension
sudo -u postgres psql -d vortex_knowledge -c "CREATE EXTENSION vector;"
```

### Setting Up MongoDB for Document Storage

MongoDB is ideal for storing unstructured data and conversation history:

```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Create database and user
mongosh --eval "use vortex_documents; db.createUser({user: 'vortex', pwd: 'your_secure_password', roles: [{role: 'readWrite', db: 'vortex_documents'}]})"
```

### Setting Up Redis for Caching

Redis provides fast in-memory caching for frequently accessed data:

```bash
# Configure Redis
sudo nano /etc/redis/redis.conf
# Set password: requirepass your_secure_password
# Save and exit

# Restart Redis
sudo systemctl restart redis-server
```

### Configuring Vortex for Local Databases

Create a database configuration file:

```bash
nano /workspace/vortex/database_config.toml
```

Add the following configuration:

```toml
[database]
# Enable database storage
enable_database_storage = true

# Vector database configuration (PostgreSQL with pgvector)
[database.vector]
type = "postgresql"
host = "localhost"
port = 5432
user = "vortex"
password = "your_secure_password"
database = "vortex_knowledge"
table_name = "embeddings"
vector_dimension = 1536  # Adjust based on your embedding model

# Document database configuration (MongoDB)
[database.document]
type = "mongodb"
uri = "mongodb://vortex:your_secure_password@localhost:27017/vortex_documents"
collection_name = "conversations"

# Cache configuration (Redis)
[database.cache]
type = "redis"
host = "localhost"
port = 6379
password = "your_secure_password"
db = 0
```

## Remote Database Setup

For production deployments, it's recommended to use managed database services or properly secured remote database servers.

### Setting Up Remote PostgreSQL with pgvector

#### Option 1: Self-hosted on a separate server

```bash
# On the database server
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Configure PostgreSQL to accept remote connections
sudo nano /etc/postgresql/14/main/postgresql.conf
# Set listen_addresses = '*'

sudo nano /etc/postgresql/14/main/pg_hba.conf
# Add: host vortex_knowledge vortex your_vortex_server_ip/32 md5

# Install pgvector extension (as shown in local setup)

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Option 2: Using a managed service (AWS RDS with pgvector)

1. Create a PostgreSQL RDS instance in AWS
2. Enable the pgvector extension using a parameter group
3. Configure security groups to allow connections from your Vortex server

### Setting Up Remote MongoDB

#### Option 1: Self-hosted on a separate server

```bash
# On the database server
# Install MongoDB (as shown in local setup)

# Configure MongoDB to accept remote connections
sudo nano /etc/mongod.conf
# Set bindIp: 0.0.0.0

# Enable authentication
# security:
#   authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod
```

#### Option 2: Using MongoDB Atlas

1. Create a MongoDB Atlas account
2. Set up a new cluster
3. Create a database user with appropriate permissions
4. Whitelist your Vortex server IP address
5. Get the connection string for your application

### Setting Up Remote Redis

#### Option 1: Self-hosted on a separate server

```bash
# On the database server
# Install Redis (as shown in local setup)

# Configure Redis to accept remote connections
sudo nano /etc/redis/redis.conf
# Set bind 0.0.0.0
# Set requirepass your_secure_password
# Set protected-mode no

# Restart Redis
sudo systemctl restart redis-server
```

#### Option 2: Using Redis Cloud

1. Create a Redis Cloud account
2. Set up a new subscription
3. Create a database
4. Get the endpoint and credentials

### Configuring Vortex for Remote Databases

Update your database configuration file:

```toml
[database]
enable_database_storage = true

# Vector database configuration (Remote PostgreSQL with pgvector)
[database.vector]
type = "postgresql"
host = "your_postgresql_server_ip_or_endpoint"
port = 5432
user = "vortex"
password = "your_secure_password"
database = "vortex_knowledge"
table_name = "embeddings"
vector_dimension = 1536
ssl_mode = "require"  # For secure connections

# Document database configuration (MongoDB Atlas)
[database.document]
type = "mongodb"
uri = "mongodb+srv://vortex:your_secure_password@your-cluster.mongodb.net/vortex_documents"
collection_name = "conversations"

# Cache configuration (Redis Cloud)
[database.cache]
type = "redis"
host = "your_redis_endpoint"
port = 6379
password = "your_secure_password"
db = 0
ssl = true
```

## Vector Database for Knowledge Storage

The vector database is crucial for Vortex's knowledge retrieval capabilities. It stores embeddings of text that can be semantically searched.

### Schema Setup for PostgreSQL with pgvector

```sql
-- Connect to the database
\c vortex_knowledge

-- Create embeddings table
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- Adjust dimension based on your model
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an index for faster similarity search
CREATE INDEX ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### Python Integration Code

```python
import psycopg2
from psycopg2.extras import Json
import numpy as np

class VectorDatabase:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        
    def store_embedding(self, content, embedding, metadata=None):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO embeddings (content, embedding, metadata) VALUES (%s, %s, %s) RETURNING id",
                (content, embedding, Json(metadata) if metadata else None)
            )
            id = cur.fetchone()[0]
            self.conn.commit()
            return id
            
    def search_similar(self, query_embedding, limit=5):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, content, metadata, 1 - (embedding <=> %s) AS similarity FROM embeddings ORDER BY embedding <=> %s LIMIT %s",
                (query_embedding, query_embedding, limit)
            )
            return cur.fetchall()
```

## Document Database for Unstructured Data

The document database stores conversation history, agent states, and other unstructured data.

### Collections Setup for MongoDB

```javascript
// Connect to MongoDB
use vortex_documents

// Create collections with validation
db.createCollection("conversations", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["session_id", "events", "created_at"],
         properties: {
            session_id: {
               bsonType: "string",
               description: "Session identifier"
            },
            events: {
               bsonType: "array",
               description: "Array of conversation events"
            },
            created_at: {
               bsonType: "date",
               description: "Creation timestamp"
            },
            updated_at: {
               bsonType: "date",
               description: "Last update timestamp"
            }
         }
      }
   }
})

// Create indexes
db.conversations.createIndex({ "session_id": 1 }, { unique: true })
db.conversations.createIndex({ "created_at": 1 })
```

### Python Integration Code

```python
from pymongo import MongoClient
from datetime import datetime

class DocumentDatabase:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.get_database()
        self.conversations = self.db.conversations
        
    def store_conversation(self, session_id, events):
        now = datetime.utcnow()
        result = self.conversations.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "events": events,
                    "updated_at": now
                },
                "$setOnInsert": {
                    "created_at": now
                }
            },
            upsert=True
        )
        return result.upserted_id or session_id
        
    def get_conversation(self, session_id):
        return self.conversations.find_one({"session_id": session_id})
```

## Relational Database for Structured Data

A relational database stores user information, system configuration, and other structured data.

### Schema Setup for PostgreSQL

```sql
-- Connect to the database
\c vortex_knowledge

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- Create sessions table
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB
);

-- Create configurations table
CREATE TABLE configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    config_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, name)
);
```

### Python Integration Code

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    sessions = relationship("Session", back_populates="user")
    configurations = relationship("Configuration", back_populates="user")

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    metadata = Column(JSON)
    
    user = relationship("User", back_populates="sessions")

class Configuration(Base):
    __tablename__ = 'configurations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    config_data = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="configurations")

class RelationalDatabase:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_user(self, username, email, password_hash):
        session = self.Session()
        user = User(username=username, email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        user_id = user.id
        session.close()
        return user_id
```

## Database Integration with Memory System

Vortex's memory system can be integrated with the databases to provide persistent storage and efficient retrieval.

### Memory System Configuration

```toml
[memory]
# Memory system type
type = "database"

# Memory persistence
persistence = true
persistence_path = ""  # Empty means use database

# Vector database integration
use_vector_db = true
vector_db_config = "database.vector"

# Document database integration
use_document_db = true
document_db_config = "database.document"

# Cache integration
use_cache = true
cache_config = "database.cache"

# Memory parameters
max_tokens = 100000
decay_rate = 0.01
importance_threshold = 0.5
```

### Integration with Amortized Forgetting Condenser

The Amortized Forgetting Condenser can use the vector database to store and retrieve memories based on importance:

```python
from openhands.memory.condensers.amortized_forgetting import AmortizedForgettingCondenser

class DatabaseAmortizedForgettingCondenser(AmortizedForgettingCondenser):
    def __init__(self, vector_db, **kwargs):
        super().__init__(**kwargs)
        self.vector_db = vector_db
        
    def store_memory(self, content, importance, metadata=None):
        # Get embedding from content
        embedding = self.get_embedding(content)
        
        # Store in vector database with importance as metadata
        metadata = metadata or {}
        metadata['importance'] = importance
        self.vector_db.store_embedding(content, embedding, metadata)
        
    def retrieve_relevant_memories(self, query, limit=5):
        # Get embedding from query
        query_embedding = self.get_embedding(query)
        
        # Search vector database
        results = self.vector_db.search_similar(query_embedding, limit)
        
        # Return memories sorted by similarity and importance
        return [
            {
                'content': result[1],
                'metadata': result[2],
                'similarity': result[3]
            }
            for result in results
        ]
```

## Backup and Recovery Strategies

### PostgreSQL Backup

```bash
# Create a backup script
nano /home/user/backup_postgres.sh
```

Add the following content:

```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/path/to/backups/postgresql"
DB_NAME="vortex_knowledge"
DB_USER="vortex"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER -d $DB_NAME -F c -f $BACKUP_DIR/vortex_knowledge_$TIMESTAMP.dump

# Keep only the last 7 backups
ls -tp $BACKUP_DIR/*.dump | grep -v '/$' | tail -n +8 | xargs -I {} rm -- {}
```

Make it executable:

```bash
chmod +x /home/user/backup_postgres.sh
```

Set up a cron job:

```bash
crontab -e
# Add: 0 2 * * * /home/user/backup_postgres.sh
```

### MongoDB Backup

```bash
# Create a backup script
nano /home/user/backup_mongodb.sh
```

Add the following content:

```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/path/to/backups/mongodb"
DB_NAME="vortex_documents"
DB_USER="vortex"
DB_PASSWORD="your_secure_password"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
mongodump --uri="mongodb://$DB_USER:$DB_PASSWORD@localhost:27017/$DB_NAME" --out=$BACKUP_DIR/vortex_documents_$TIMESTAMP

# Compress backup
tar -czf $BACKUP_DIR/vortex_documents_$TIMESTAMP.tar.gz -C $BACKUP_DIR vortex_documents_$TIMESTAMP
rm -rf $BACKUP_DIR/vortex_documents_$TIMESTAMP

# Keep only the last 7 backups
ls -tp $BACKUP_DIR/*.tar.gz | grep -v '/$' | tail -n +8 | xargs -I {} rm -- {}
```

Make it executable:

```bash
chmod +x /home/user/backup_mongodb.sh
```

Set up a cron job:

```bash
crontab -e
# Add: 0 3 * * * /home/user/backup_mongodb.sh
```

### Recovery Procedures

#### PostgreSQL Recovery

```bash
# Restore from backup
pg_restore -U vortex -d vortex_knowledge -c /path/to/backups/postgresql/vortex_knowledge_20250419_120000.dump
```

#### MongoDB Recovery

```bash
# Extract backup
tar -xzf /path/to/backups/mongodb/vortex_documents_20250419_120000.tar.gz -C /tmp

# Restore from backup
mongorestore --uri="mongodb://vortex:your_secure_password@localhost:27017/vortex_documents" --drop /tmp/vortex_documents_20250419_120000/vortex_documents
```

## Performance Optimization

### PostgreSQL Optimization

```sql
-- Increase shared_buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '4GB';

-- Increase work_mem for complex queries
ALTER SYSTEM SET work_mem = '64MB';

-- Optimize for SSD storage
ALTER SYSTEM SET random_page_cost = 1.1;

-- Increase max_connections
ALTER SYSTEM SET max_connections = 200;

-- Reload configuration
SELECT pg_reload_conf();
```

### MongoDB Optimization

```javascript
// Create compound indexes for common queries
db.conversations.createIndex({ "session_id": 1, "created_at": -1 })

// Create text index for content search
db.conversations.createIndex({ "events.content": "text" })

// Set write concern for better performance
db.conversations.updateMany({}, { $set: { newField: "value" } }, { writeConcern: { w: 1, j: false } })
```

### Redis Optimization

Edit `/etc/redis/redis.conf`:

```
# Memory management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Performance
tcp-keepalive 60
```

## Security Best Practices

### PostgreSQL Security

```sql
-- Create a read-only user for analytics
CREATE USER vortex_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE vortex_knowledge TO vortex_readonly;
GRANT USAGE ON SCHEMA public TO vortex_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO vortex_readonly;

-- Encrypt sensitive data
CREATE EXTENSION pgcrypto;
UPDATE users SET email = pgp_sym_encrypt(email, 'encryption_key');

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/path/to/server.crt';
ALTER SYSTEM SET ssl_key_file = '/path/to/server.key';
```

### MongoDB Security

```javascript
// Enable authentication
use admin
db.createUser({
  user: "admin",
  pwd: "secure_admin_password",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

// Create application user with specific permissions
use vortex_documents
db.createUser({
  user: "vortex_app",
  pwd: "app_specific_password",
  roles: [ { role: "readWrite", db: "vortex_documents" } ]
})

// Enable encryption for sensitive fields
db.conversations.updateMany(
  {},
  [{ $set: { 
      "events": { 
        $map: { 
          input: "$events", 
          in: { 
            $mergeObjects: [ 
              "$$this", 
              { 
                "content": { 
                  $cond: { 
                    if: { $eq: ["$$this.type", "sensitive"] }, 
                    then: { $function: { 
                      body: function(text) { 
                        return text; // Replace with actual encryption in production
                      }, 
                      args: ["$$this.content"], 
                      lang: "js" 
                    }}, 
                    else: "$$this.content" 
                  } 
                } 
              } 
            ] 
          } 
        } 
      } 
    }}]
)
```

### Redis Security

```bash
# Configure Redis for enhanced security
sudo nano /etc/redis/redis.conf
```

Add/modify these settings:

```
# Bind to localhost only if not using remote access
bind 127.0.0.1

# Set a strong password
requirepass your_very_strong_password

# Disable dangerous commands
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command SHUTDOWN ""

# Enable TLS/SSL
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

### Network Security

```bash
# Configure firewall to restrict database access
sudo ufw allow from your_vortex_server_ip to any port 5432 proto tcp
sudo ufw allow from your_vortex_server_ip to any port 27017 proto tcp
sudo ufw allow from your_vortex_server_ip to any port 6379 proto tcp
```

## Conclusion

This comprehensive guide covers all aspects of setting up and configuring databases for the Vortex framework. By following these instructions, you can create a robust, scalable, and secure database infrastructure for your Vortex deployment, whether local or remote.

Remember to:
- Regularly back up your databases
- Monitor performance and optimize as needed
- Keep your database software updated
- Follow security best practices
- Adjust configurations based on your specific workload and hardware

With properly configured databases, your Vortex instance will have enhanced knowledge storage capabilities, improved performance, and reliable data persistence.