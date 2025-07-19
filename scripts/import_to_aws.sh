#!/bin/bash

# AWS RDS Meeting Import Helper Script
# This script provides a convenient wrapper for importing meetings to AWS RDS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPORT_SCRIPT="$SCRIPT_DIR/import_meetings_to_aws_rds.py"
LOG_FILE="meeting_import.log"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
AWS RDS Meeting Import Helper Script

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -u, --aws-db-url URL    AWS RDS database URL (required)
    -l, --local-db-url URL  Local database URL (optional)
    -s, --source TYPE       Data source type: local_db, csv, json, pdf_dir, scrape
    -f, --file PATH         File path (for csv/json sources)
    -d, --directory PATH    Directory path (for pdf_dir source)
    --days-ahead N          Days ahead to scrape (default: 30)
    --create-tables         Create database tables if they don't exist
    --test-only             Test connection only
    --stats-only            Show statistics only
    --dry-run               Show what would be imported without actually importing

Examples:
    # Test connection
    $0 --aws-db-url "postgresql://admin:pass@rds-endpoint:5432/db" --test-only

    # Import from local database
    $0 --aws-db-url "postgresql://admin:pass@rds-endpoint:5432/db" \\
       --local-db-url "postgresql://user:pass@localhost:5435/citycamp_db" \\
       --source local_db --create-tables

    # Import from CSV file
    $0 --aws-db-url "postgresql://admin:pass@rds-endpoint:5432/db" \\
       --source csv --file meetings.csv

    # Import from PDF directory
    $0 --aws-db-url "postgresql://admin:pass@rds-endpoint:5432/db" \\
       --source pdf_dir --directory ./meeting_pdfs

Environment Variables:
    AWS_RDS_URL             AWS RDS database URL
    LOCAL_DB_URL            Local database URL

EOF
}

# Parse command line arguments
AWS_DB_URL=""
LOCAL_DB_URL=""
SOURCE=""
FILE=""
DIRECTORY=""
DAYS_AHEAD=30
CREATE_TABLES=false
TEST_ONLY=false
STATS_ONLY=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -u|--aws-db-url)
            AWS_DB_URL="$2"
            shift 2
            ;;
        -l|--local-db-url)
            LOCAL_DB_URL="$2"
            shift 2
            ;;
        -s|--source)
            SOURCE="$2"
            shift 2
            ;;
        -f|--file)
            FILE="$2"
            shift 2
            ;;
        -d|--directory)
            DIRECTORY="$2"
            shift 2
            ;;
        --days-ahead)
            DAYS_AHEAD="$2"
            shift 2
            ;;
        --create-tables)
            CREATE_TABLES=true
            shift
            ;;
        --test-only)
            TEST_ONLY=true
            shift
            ;;
        --stats-only)
            STATS_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check for environment variables if not provided
if [[ -z "$AWS_DB_URL" ]] && [[ -n "$AWS_RDS_URL" ]]; then
    AWS_DB_URL="$AWS_RDS_URL"
fi

if [[ -z "$LOCAL_DB_URL" ]] && [[ -n "$LOCAL_DB_URL" ]]; then
    LOCAL_DB_URL="$LOCAL_DB_URL"
fi

# Validate required parameters
if [[ -z "$AWS_DB_URL" ]]; then
    print_error "AWS RDS database URL is required"
    print_error "Use --aws-db-url or set AWS_RDS_URL environment variable"
    exit 1
fi

# Check if import script exists
if [[ ! -f "$IMPORT_SCRIPT" ]]; then
    print_error "Import script not found: $IMPORT_SCRIPT"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Function to run the import script
run_import() {
    local cmd="python3 $IMPORT_SCRIPT --aws-db-url \"$AWS_DB_URL\""

    if [[ -n "$LOCAL_DB_URL" ]]; then
        cmd="$cmd --local-db-url \"$LOCAL_DB_URL\""
    fi

    if [[ "$CREATE_TABLES" == true ]]; then
        cmd="$cmd --create-tables"
    fi

    if [[ "$TEST_ONLY" == true ]]; then
        cmd="$cmd --test-connection"
    elif [[ "$STATS_ONLY" == true ]]; then
        cmd="$cmd --stats"
    elif [[ -n "$SOURCE" ]]; then
        cmd="$cmd --source $SOURCE"

        if [[ -n "$FILE" ]]; then
            cmd="$cmd --file \"$FILE\""
        fi

        if [[ -n "$DIRECTORY" ]]; then
            cmd="$cmd --directory \"$DIRECTORY\""
        fi

        if [[ "$SOURCE" == "scrape" ]]; then
            cmd="$cmd --days-ahead $DAYS_AHEAD"
        fi
    fi

    if [[ "$DRY_RUN" == true ]]; then
        print_status "Would run: $cmd"
        return 0
    fi

    print_status "Running: $cmd"
    eval "$cmd"
}

# Main execution
print_status "Starting AWS RDS Meeting Import Process"
print_status "Log file: $LOG_FILE"

# Validate source-specific requirements
if [[ "$TEST_ONLY" == false ]] && [[ "$STATS_ONLY" == false ]] && [[ -z "$SOURCE" ]]; then
    print_error "Source type is required when not testing connection or showing stats"
    print_error "Use --source with one of: local_db, csv, json, pdf_dir, scrape"
    exit 1
fi

if [[ "$SOURCE" == "csv" ]] || [[ "$SOURCE" == "json" ]]; then
    if [[ -z "$FILE" ]]; then
        print_error "File path is required for $SOURCE source"
        exit 1
    fi
    if [[ ! -f "$FILE" ]]; then
        print_error "File not found: $FILE"
        exit 1
    fi
fi

if [[ "$SOURCE" == "pdf_dir" ]]; then
    if [[ -z "$DIRECTORY" ]]; then
        print_error "Directory path is required for pdf_dir source"
        exit 1
    fi
    if [[ ! -d "$DIRECTORY" ]]; then
        print_error "Directory not found: $DIRECTORY"
        exit 1
    fi
fi

# Check Python dependencies
print_status "Checking Python dependencies..."
python3 -c "import sqlalchemy, psycopg2, pdfplumber" 2>/dev/null || {
    print_error "Missing Python dependencies"
    print_error "Install with: pip install sqlalchemy psycopg2-binary pdfplumber"
    exit 1
}

# Run the import
if [[ "$DRY_RUN" == true ]]; then
    print_status "DRY RUN MODE - No actual import will be performed"
fi

start_time=$(date)
print_status "Started at: $start_time"

if run_import; then
    end_time=$(date)
    print_success "Import completed successfully!"
    print_success "Started: $start_time"
    print_success "Finished: $end_time"

    if [[ -f "$LOG_FILE" ]]; then
        print_status "Check $LOG_FILE for detailed logs"
    fi
else
    print_error "Import failed!"
    if [[ -f "$LOG_FILE" ]]; then
        print_error "Check $LOG_FILE for error details"
        print_error "Last few lines of log:"
        tail -n 10 "$LOG_FILE" 2>/dev/null || true
    fi
    exit 1
fi
