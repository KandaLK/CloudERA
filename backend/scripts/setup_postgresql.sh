#!/bin/bash

# PostgreSQL Setup Script for Cloud ERA
# This script automates the PostgreSQL database setup process

set -e  # Exit on any error

echo "🚀 Cloud ERA PostgreSQL Setup Script"
echo "====================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Database configuration
DB_NAME="cloud-web"
DB_USER="cloud_era_user"
DB_PASSWORD="cloud_era_password"
DB_HOST="localhost"
DB_PORT="5432"

echo -e "${BLUE}Step 1: Checking PostgreSQL installation...${NC}"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed!${NC}"
    echo "Please install PostgreSQL 16 first:"
    echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
    echo "  macOS: brew install postgresql@16"
    echo "  Windows: Download from https://www.postgresql.org/download/windows/"
    exit 1
fi

PSQL_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
echo -e "${GREEN}✅ PostgreSQL $PSQL_VERSION is installed${NC}"

echo -e "${BLUE}Step 2: Checking PostgreSQL service...${NC}"

# Check if PostgreSQL service is running
if ! pgrep -x "postgres" > /dev/null; then
    echo -e "${YELLOW}⚠️ PostgreSQL service is not running${NC}"
    echo "Starting PostgreSQL service..."
    
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
    elif command -v brew &> /dev/null; then
        brew services start postgresql@16
    else
        echo -e "${RED}❌ Cannot start PostgreSQL service automatically${NC}"
        echo "Please start PostgreSQL manually and run this script again"
        exit 1
    fi
fi

echo -e "${GREEN}✅ PostgreSQL service is running${NC}"

echo -e "${BLUE}Step 3: Creating database and user...${NC}"

# Create database and user using the SQL script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/create_database.sql" ]; then
    sudo -u postgres psql -f "$SCRIPT_DIR/create_database.sql"
    echo -e "${GREEN}✅ Database and user created successfully${NC}"
else
    echo -e "${RED}❌ create_database.sql not found in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Step 4: Creating tables and indexes...${NC}"

# Create tables using the SQL script
if [ -f "$SCRIPT_DIR/create_tables.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h $DB_HOST -p $DB_PORT -f "$SCRIPT_DIR/create_tables.sql"
    echo -e "${GREEN}✅ Tables and indexes created successfully${NC}"
else
    echo -e "${RED}❌ create_tables.sql not found in $SCRIPT_DIR${NC}"
    exit 1
fi

echo -e "${BLUE}Step 5: Verifying database connection...${NC}"

# Test database connection
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h $DB_HOST -p $DB_PORT -c "SELECT 'Connection successful!' as message;"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database connection verified${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

echo -e "${BLUE}Step 6: Updating environment configuration...${NC}"

# Update .env file if it exists
ENV_FILE="$(dirname "$SCRIPT_DIR")/../.env"
if [ -f "$ENV_FILE" ]; then
    # Backup original .env
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update database URL in .env
    DB_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
    
    if grep -q "BACKEND_DATABASE_URL=" "$ENV_FILE"; then
        sed -i.bak "s|^BACKEND_DATABASE_URL=.*|BACKEND_DATABASE_URL=$DB_URL|" "$ENV_FILE"
        echo -e "${GREEN}✅ Environment file updated${NC}"
    else
        echo "BACKEND_DATABASE_URL=$DB_URL" >> "$ENV_FILE"
        echo -e "${GREEN}✅ Database URL added to environment file${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ .env file not found, please update manually${NC}"
fi

echo ""
echo -e "${GREEN}🎉 PostgreSQL setup completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Initialize sample data: python scripts/init_database.py"
echo "3. Start the backend server: python main.py"
echo ""
echo "Database connection details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  Username: $DB_USER"
echo "  Connection URL: postgresql://$DB_USER:***@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"