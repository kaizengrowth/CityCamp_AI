#!/bin/bash

# CityCamp AI - Seed Local Data to AWS RDS
# Follow these steps to import your 44 local meetings to AWS

echo "🚀 CityCamp AI - AWS Data Seeding Guide"
echo "========================================"
echo ""

echo "Step 1: Set your AWS RDS credentials (EDIT THESE WITH YOUR ACTUAL VALUES):"
echo "export AWS_RDS_HOST=\"your-rds-cluster.cluster-xxxxx.us-east-1.rds.amazonaws.com\""
echo "export AWS_RDS_DATABASE=\"citycamp_ai\""
echo "export AWS_RDS_USERNAME=\"your-username\""
echo "export AWS_RDS_PASSWORD=\"your-password\""
echo ""

echo "Step 2: Test the connection:"
echo "./import_to_aws.sh \\"
echo "  --aws-db-url \"postgresql://\$AWS_RDS_USERNAME:\$AWS_RDS_PASSWORD@\$AWS_RDS_HOST:5432/\$AWS_RDS_DATABASE\" \\"
echo "  --test-only"
echo ""

echo "Step 3: Import your 44 meetings from local database:"
echo "./import_to_aws.sh \\"
echo "  --aws-db-url \"postgresql://\$AWS_RDS_USERNAME:\$AWS_RDS_PASSWORD@\$AWS_RDS_HOST:5432/\$AWS_RDS_DATABASE\" \\"
echo "  --local-db-url \"postgresql://postgres:password@localhost:5432/citycamp_db\" \\"
echo "  --source local_db"
echo ""

echo "Step 4: Verify the import:"
echo "python simple_rds_test.py"
echo ""

echo "Note: Make sure your local database is running on localhost:5432"
echo "If it's running on a different port, adjust the --local-db-url accordingly"
