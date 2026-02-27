#!/bin/bash
# Keystone Nexus - Environment Setup Script
# NTU M2G6 Module 2 Project

set -e  # Exit on error

echo "🚀 Keystone Nexus Setup Starting..."

# ===========================================
# 1. Python Virtual Environment
# ===========================================
echo "📦 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# ===========================================
# 2. Install Python Dependencies
# ===========================================
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# ===========================================
# 3. AWS CLI Configuration Check
# ===========================================
echo "☁️  Checking AWS CLI configuration..."
if ! aws sts get-caller-identity &>/dev/null; then
    echo "⚠️  AWS credentials not configured"
    echo "Run: aws configure"
    echo "Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
else
    echo "✅ AWS credentials configured"
    aws sts get-caller-identity
fi

# ===========================================
# 4. Create AWS S3 Buckets (if needed)
# ===========================================
echo "🪣 Creating S3 buckets..."
BUCKETS=(
    "olist-data-lake-bronze"
    "olist-data-lake-silver"
    "olist-data-lake-gold"
    "olist-data-lake-quarantine"
)

for BUCKET in "${BUCKETS[@]}"; do
    if aws s3 ls "s3://$BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
        echo "Creating bucket: $BUCKET"
        aws s3 mb "s3://$BUCKET" --region ap-southeast-1 || echo "⚠️  Failed to create $BUCKET (may already exist)"
    else
        echo "✅ Bucket already exists: $BUCKET"
    fi
done

# ===========================================
# 5. Create Directory Structure
# ===========================================
echo "📁 Creating project directories..."
mkdir -p data/{bronze,silver,gold,quarantine}
mkdir -p logs
mkdir -p src/{ingestion,transformation,validation,analytics}
mkdir -p dags
mkdir -p tests
mkdir -p analysis
mkdir -p docs
mkdir -p config

echo "✅ Directory structure created"

# ===========================================
# 6. Download Olist Dataset (Kaggle)
# ===========================================
echo "📥 Checking for Olist dataset..."
if [ ! -f "data/olist_orders_dataset.csv" ]; then
    echo "⚠️  Olist dataset not found in data/"
    echo "Download manually from: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce"
    echo "Or use Kaggle API:"
    echo "  kaggle datasets download -d olistbr/brazilian-ecommerce"
    echo "  unzip brazilian-ecommerce.zip -d data/"
else
    echo "✅ Olist dataset found"
fi

# ===========================================
# 7. Setup Configuration
# ===========================================
echo "⚙️  Creating configuration files..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Keystone Nexus Environment Configuration

# AWS Configuration
AWS_REGION=ap-southeast-1
AWS_PROFILE=default

# S3 Buckets
S3_BRONZE_BUCKET=olist-data-lake-bronze
S3_SILVER_BUCKET=olist-data-lake-silver
S3_GOLD_BUCKET=olist-data-lake-gold
S3_QUARANTINE_BUCKET=olist-data-lake-quarantine

# Database (RDS PostgreSQL for Airflow)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=airflow_db
DB_USER=airflow
DB_PASSWORD=changeme

# Kafka (if using streaming ingestion)
KAFKA_BROKERS=10.0.1.50:9092
KAFKA_TOPIC=olist-enterprise-events

# Athena Configuration
ATHENA_DATABASE=olist_silver
ATHENA_WORKGROUP=primary
ATHENA_OUTPUT_LOCATION=s3://olist-data-lake-gold/athena-results/

# Great Expectations
GE_DATA_CONTEXT_ROOT=/path/to/great_expectations/

# Feature Flags
USE_STREAMING_INGESTION=false
USE_CPP_GRPC_LAYER=false
USE_MANAGED_AIRFLOW=false

# Logging
LOG_LEVEL=INFO
EOF
    echo "✅ .env file created (edit with your actual credentials)"
else
    echo "⚠️  .env file already exists"
fi

# ===========================================
# 8. Summary
# ===========================================
echo ""
echo "🎉 Keystone Nexus Setup Complete!"
echo ""
echo "Next Steps:"
echo "1. Edit .env file with your AWS credentials"
echo "2. Download Olist dataset to data/ directory"
echo "3. Run ingestion script: python src/ingestion/ingest_to_bronze.py"
echo "4. Setup dbt project: dbt init"
echo "5. Configure Airflow: airflow db init"
echo ""
echo "To activate environment: source venv/bin/activate"
echo ""
