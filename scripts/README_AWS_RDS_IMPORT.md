# AWS RDS Meeting Import Script

This script imports meeting data from various sources into AWS RDS PostgreSQL database. It supports multiple data sources and provides comprehensive error handling and logging.

## Features

- **Multiple Data Sources**: Import from local PostgreSQL, CSV files, JSON files, PDF directories, or direct web scraping
- **AWS RDS Integration**: Optimized for AWS RDS PostgreSQL with proper connection handling
- **Error Handling**: Comprehensive error handling with detailed logging
- **Duplicate Prevention**: Automatically skips existing meetings based on external_id
- **Batch Processing**: Processes data in batches for better performance
- **Statistics**: Provides detailed import statistics and progress tracking

## Prerequisites

1. **Python Dependencies**: Install required packages
   ```bash
   pip install sqlalchemy psycopg2-binary pdfplumber pandas
   ```

2. **AWS RDS Setup**: Ensure your AWS RDS PostgreSQL instance is running and accessible
   - Security groups allow connections from your IP
   - Database user has appropriate permissions
   - SSL is configured if required

3. **Network Access**: Ensure your machine can connect to AWS RDS
   - VPC settings allow external connections (if needed)
   - Firewall rules permit PostgreSQL connections

## Usage

### Basic Syntax
```bash
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://username:password@rds-endpoint:5432/dbname" --source SOURCE_TYPE [additional options]
```

### 1. Import from Local PostgreSQL Database
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://admin:password@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai" \
  --local-db-url "postgresql://user:password@localhost:5435/citycamp_db" \
  --source local_db \
  --create-tables
```

### 2. Import from CSV File
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://admin:password@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai" \
  --source csv \
  --file meetings.csv \
  --create-tables
```

### 3. Import from JSON File
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://admin:password@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai" \
  --source json \
  --file meetings.json \
  --create-tables
```

### 4. Import from PDF Directory
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://admin:password@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai" \
  --source pdf_dir \
  --directory ./meeting_pdfs \
  --create-tables
```

### 5. Import from Web Scraping
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://admin:password@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai" \
  --source scrape \
  --days-ahead 60 \
  --create-tables
```

## Data Format Requirements

### CSV Format
Use the provided `meetings_template.csv` as a reference. Required columns:
- `title`: Meeting title
- `meeting_date`: ISO format datetime (e.g., "2024-01-15T16:00:00")
- `meeting_type`: Type of meeting (e.g., "city_council", "special_meeting")

Optional columns:
- `description`, `location`, `meeting_url`, `agenda_url`, `minutes_url`, `status`, `external_id`, `topics`, `keywords`, `summary`

### JSON Format
```json
{
  "meetings": [
    {
      "title": "City Council Meeting",
      "meeting_date": "2024-01-15T16:00:00",
      "meeting_type": "city_council",
      "description": "Regular meeting",
      "location": "City Hall",
      "status": "completed",
      "agenda_items": [
        {
          "title": "Budget Discussion",
          "description": "Annual budget review",
          "item_type": "discussion"
        }
      ]
    }
  ]
}
```

### PDF Filename Format
PDFs should follow the naming convention:
- `YY-XXX-Z_YY-XXX-Z YYYY-MM-DD HH:MM Minutes.pdf`
- `YY-XXX-Z_YY-XXX-Z YYYY-MM-DD Special Meeting Minutes.pdf`

Examples:
- `24-1148-1_24-1148-1 2024-11-06 4PM Minutes.pdf`
- `24-1157-1_24-1157-1 2024-12-02 Special Meeting Minutes.pdf`

## Command Line Options

| Option | Description | Required | Default |
|--------|-------------|----------|---------|
| `--aws-db-url` | AWS RDS PostgreSQL connection URL | Yes | - |
| `--source` | Data source type (local_db, csv, json, pdf_dir, scrape) | Yes | - |
| `--local-db-url` | Local PostgreSQL URL (for local_db source) | No | Default local URL |
| `--file` | File path (for csv/json sources) | Conditional | - |
| `--directory` | Directory path (for pdf_dir source) | Conditional | - |
| `--days-ahead` | Days to scrape ahead (for scrape source) | No | 30 |
| `--create-tables` | Create database tables if they don't exist | No | False |
| `--test-connection` | Test AWS RDS connection and exit | No | False |
| `--stats` | Show import statistics and exit | No | False |

## Configuration

### Environment Variables
You can set these environment variables instead of passing them in the URL:
```bash
export AWS_RDS_HOST="citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com"
export AWS_RDS_PORT="5432"
export AWS_RDS_DATABASE="citycamp_ai"
export AWS_RDS_USERNAME="admin"
export AWS_RDS_PASSWORD="your_password"
```

### AWS RDS Connection URL Format
```
postgresql://username:password@endpoint:port/database_name?sslmode=require
```

Example:
```
postgresql://admin:mypassword@citycamp-ai.cluster-xxxxx.us-east-1.rds.amazonaws.com:5432/citycamp_ai?sslmode=require
```

## Security Best Practices

1. **Use Environment Variables**: Store sensitive credentials in environment variables
2. **Enable SSL**: Always use SSL connections to AWS RDS
3. **Least Privilege**: Use database users with minimal required permissions
4. **Network Security**: Use VPC security groups to restrict access
5. **Credential Rotation**: Regularly rotate database passwords

## Troubleshooting

### Connection Issues
```bash
# Test connection only
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://..." \
  --test-connection
```

### Common Errors

1. **Connection Timeout**
   - Check security groups allow your IP
   - Verify RDS endpoint is correct
   - Ensure RDS instance is running

2. **Authentication Failed**
   - Verify username and password
   - Check if user exists in RDS
   - Ensure user has required permissions

3. **SSL Certificate Error**
   - Add `?sslmode=require` to connection URL
   - Download and configure RDS CA certificate if needed

4. **Permission Denied**
   - Ensure database user has CREATE, INSERT, UPDATE permissions
   - Check if user can access the specified database

### Logging
The script creates detailed logs in `meeting_import.log`. Check this file for:
- Connection status
- Import progress
- Error details
- Statistics

## Performance Optimization

1. **Batch Size**: The script processes data in batches of 10 by default
2. **Connection Pooling**: Uses SQLAlchemy connection pooling
3. **Duplicate Checking**: Efficiently checks for existing meetings
4. **Transaction Management**: Uses transactions for data consistency

## Monitoring Import Progress

### View Statistics
```bash
python import_meetings_to_aws_rds.py \
  --aws-db-url "postgresql://..." \
  --stats
```

### Monitor Log File
```bash
tail -f meeting_import.log
```

## Database Schema

The script creates these tables:
- `meetings`: Main meeting information
- `agenda_items`: Meeting agenda items
- `meeting_categories`: Meeting categories

See `backend/app/models/meeting.py` for complete schema definitions.

## Examples

### Complete Import Workflow
```bash
# 1. Test connection
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://..." --test-connection

# 2. Create tables
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://..." --source local_db --create-tables

# 3. Import from local database
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://..." --source local_db

# 4. Import additional data from CSV
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://..." --source csv --file new_meetings.csv

# 5. Check final statistics
python import_meetings_to_aws_rds.py --aws-db-url "postgresql://..." --stats
```

### Automated Script
```bash
#!/bin/bash
set -e

AWS_DB_URL="postgresql://admin:password@rds-endpoint:5432/citycamp_ai"

echo "Testing AWS RDS connection..."
python import_meetings_to_aws_rds.py --aws-db-url "$AWS_DB_URL" --test-connection

echo "Creating tables..."
python import_meetings_to_aws_rds.py --aws-db-url "$AWS_DB_URL" --source local_db --create-tables

echo "Importing from local database..."
python import_meetings_to_aws_rds.py --aws-db-url "$AWS_DB_URL" --source local_db

echo "Importing from PDFs..."
python import_meetings_to_aws_rds.py --aws-db-url "$AWS_DB_URL" --source pdf_dir --directory ./pdfs

echo "Final statistics:"
python import_meetings_to_aws_rds.py --aws-db-url "$AWS_DB_URL" --stats

echo "Import completed successfully!"
```

## Support

For issues or questions:
1. Check the log file for detailed error messages
2. Verify AWS RDS configuration and connectivity
3. Ensure all dependencies are installed
4. Review the troubleshooting section above
