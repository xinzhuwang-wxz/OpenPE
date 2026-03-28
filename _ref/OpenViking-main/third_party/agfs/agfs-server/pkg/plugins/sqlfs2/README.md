# SQLFS2 Plugin - Plan 9 Style SQL File System

A session-based SQL interface inspired by Plan 9's file system philosophy. Execute SQL queries by reading and writing virtual files.

## Features

- **Plan 9 Style Interface**: Control databases through file operations
- **Session-based Operations**: Each session maintains its own transaction context
- **Multiple Session Levels**: Root, database, and table-bound sessions
- **JSON Data Import**: Bulk insert data via the `data` file
- **Transaction Support**: Sessions operate within database transactions
- **Multiple Backends**: SQLite, MySQL, TiDB

## Directory Structure

```
/sqlfs2/
├── ctl                           # Root-level session control
├── <sid>/                        # Root-level session directory
│   ├── ctl                       # Write "close" to close session
│   ├── query                     # Write SQL to execute
│   ├── result                    # Read query results (JSON)
│   └── error                     # Read error messages
│
└── <database>/
    ├── ctl                       # Database-level session control
    ├── <sid>/                    # Database-level session directory
    │   ├── ctl
    │   ├── query
    │   ├── result
    │   └── error
    │
    └── <table>/
        ├── ctl                   # Table-level session control
        ├── schema                # Read table schema (DDL)
        ├── count                 # Read row count
        └── <sid>/                # Table-level session directory
            ├── ctl
            ├── query
            ├── result
            ├── error
            └── data              # Write JSON to insert rows
```

## Session Levels

| Level | Path | Bound To | Files |
|-------|------|----------|-------|
| Root | `/<sid>/` | Nothing | ctl, query, result, error |
| Database | `/<db>/<sid>/` | Database | ctl, query, result, error |
| Table | `/<db>/<table>/<sid>/` | Table | ctl, query, result, error, **data** |

## Basic Usage

### Creating a Session

```bash
# Read 'ctl' to create a new session and get session ID
SID=$(cat /sqlfs2/tidb/ctl)
echo "Session ID: $SID"
```

### Executing Queries

```bash
# Write SQL to query file
echo "SELECT * FROM users WHERE id = 1" > /sqlfs2/tidb/$SID/query

# Read results (JSON format)
cat /sqlfs2/tidb/$SID/result

# Check for errors
cat /sqlfs2/tidb/$SID/error
```

### Closing a Session

```bash
# Write "close" to ctl to close the session
echo "close" > /sqlfs2/tidb/$SID/ctl
```

## The `data` File (Table-Level Sessions Only)

The `data` file is **exclusive to table-level sessions** and allows bulk JSON data insertion into the bound table.

### Why Only Table-Level?

The `data` file automatically maps JSON fields to table columns. This requires knowing the target table's schema, which is only available when the session is bound to a specific table.

### Supported JSON Formats

**1. Single Object**
```bash
echo '{"name": "Alice", "age": 30}' > /sqlfs2/tidb/mydb/users/$SID/data
```

**2. JSON Array**
```bash
echo '[{"name": "Alice"}, {"name": "Bob"}]' > /sqlfs2/tidb/mydb/users/$SID/data
```

**3. NDJSON (Newline Delimited JSON)**
```bash
cat << 'EOF' > /sqlfs2/tidb/mydb/users/$SID/data
{"name": "Alice", "age": 30}
{"name": "Bob", "age": 25}
{"name": "Charlie", "age": 35}
EOF
```

### Example: Bulk Insert

```bash
# Create table-level session
SID=$(cat /sqlfs2/tidb/mydb/users/ctl)

# Insert multiple records
cat << 'EOF' > /sqlfs2/tidb/mydb/users/$SID/data
{"id": 1, "name": "Alice", "email": "alice@example.com"}
{"id": 2, "name": "Bob", "email": "bob@example.com"}
{"id": 3, "name": "Charlie", "email": "charlie@example.com"}
EOF

# Check result
cat /sqlfs2/tidb/mydb/users/$SID/result
# Output: {"rows_affected": 3, "last_insert_id": 3}

# Close session
echo "close" > /sqlfs2/tidb/mydb/users/$SID/ctl
```

## Static Files

### Schema (Table-Level)
```bash
# Read table DDL
cat /sqlfs2/tidb/mydb/users/schema
# Output: CREATE TABLE users (id INT, name VARCHAR(255), ...)
```

### Count (Table-Level)
```bash
# Read row count
cat /sqlfs2/tidb/mydb/users/count
# Output: 42
```

## Configuration

### Static Configuration (config.yaml)

```yaml
plugins:
  sqlfs2:
    - name: tidb
      enabled: true
      path: /sqlfs2/tidb
      config:
        backend: tidb
        dsn: "user:pass@tcp(host:4000)/database?charset=utf8mb4&parseTime=True"
        session_timeout: "30m"  # Optional: auto-close idle sessions

    - name: sqlite
      enabled: true
      path: /sqlfs2/local
      config:
        backend: sqlite
        db_path: "./local.db"
```

### Dynamic Mounting

```bash
# Mount TiDB
agfs:/> mount sqlfs2 /sqlfs2/tidb backend=tidb dsn="user:pass@tcp(host:4000)/db"

# Mount SQLite
agfs:/> mount sqlfs2 /sqlfs2/local backend=sqlite db_path=/tmp/test.db
```

## HTTP API Usage

```bash
# Create session
SID=$(curl -s "http://localhost:8080/api/v1/files?path=/sqlfs2/tidb/ctl")

# Execute query (use PUT for write operations)
curl -X PUT "http://localhost:8080/api/v1/files?path=/sqlfs2/tidb/$SID/query" \
     -d "SELECT * FROM users"

# Read result
curl "http://localhost:8080/api/v1/files?path=/sqlfs2/tidb/$SID/result"

# Close session
curl -X PUT "http://localhost:8080/api/v1/files?path=/sqlfs2/tidb/$SID/ctl" \
     -d "close"
```

## Complete Example

```bash
# 1. Create database-level session
SID=$(cat /sqlfs2/tidb/ctl)
echo "Created session: $SID"

# 2. Create a table
echo "CREATE TABLE IF NOT EXISTS test_users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(255)
)" > /sqlfs2/tidb/$SID/query

# 3. Check for errors
cat /sqlfs2/tidb/$SID/error

# 4. Insert data
echo "INSERT INTO test_users (name, email) VALUES ('Alice', 'alice@test.com')" \
  > /sqlfs2/tidb/$SID/query

# 5. Query data
echo "SELECT * FROM test_users" > /sqlfs2/tidb/$SID/query
cat /sqlfs2/tidb/$SID/result
# Output:
# [
#   {
#     "id": 1,
#     "name": "Alice",
#     "email": "alice@test.com"
#   }
# ]

# 6. Close session
echo "close" > /sqlfs2/tidb/$SID/ctl
```

## Supported Query Types

| Query Type | Supported | Result Format |
|------------|-----------|---------------|
| SELECT | Yes | JSON array of objects |
| SHOW | Yes | JSON array of objects |
| DESCRIBE | Yes | JSON array of objects |
| EXPLAIN | Yes | JSON array of objects |
| INSERT | Yes | `{"rows_affected": N, "last_insert_id": N}` |
| UPDATE | Yes | `{"rows_affected": N, "last_insert_id": 0}` |
| DELETE | Yes | `{"rows_affected": N, "last_insert_id": 0}` |
| CREATE | Yes | `{"rows_affected": 0, "last_insert_id": 0}` |
| DROP | Yes | `{"rows_affected": 0, "last_insert_id": 0}` |

## Limitations

- Sessions are not persistent across server restarts
- Large result sets are fully loaded into memory
- No streaming support for query results
- The `data` file only supports INSERT operations (no UPDATE/DELETE)
- JSON field names must match column names exactly

## License

Apache License 2.0
