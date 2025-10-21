#!/bin/bash
# Database Setup Script for Health and Fitness Club Management System
# COMP3005 Final Project

echo "=========================================="
echo "Health and Fitness Club Management System"
echo "Database Setup Script"
echo "=========================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL and try again"
    exit 1
fi

# Get database credentials
read -p "Enter PostgreSQL username (default: postgres): " DB_USER
DB_USER=${DB_USER:-postgres}

read -p "Enter database name (default: fitness_club): " DB_NAME
DB_NAME=${DB_NAME:-fitness_club}

echo ""
echo "Setting up database '$DB_NAME'..."
echo ""

# Create database
echo "Step 1: Creating database..."
psql -U "$DB_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database created successfully"
else
    echo "⚠ Database might already exist or creation failed"
fi

# Create schema
echo ""
echo "Step 2: Creating database schema..."
psql -U "$DB_USER" -d "$DB_NAME" -f sql/schema.sql
if [ $? -eq 0 ]; then
    echo "✓ Schema created successfully"
else
    echo "✗ Schema creation failed"
    exit 1
fi

# Ask if user wants sample data
echo ""
read -p "Do you want to load sample data? (y/n): " LOAD_SAMPLE
if [ "$LOAD_SAMPLE" = "y" ] || [ "$LOAD_SAMPLE" = "Y" ]; then
    echo ""
    echo "Step 3: Loading sample data..."
    psql -U "$DB_USER" -d "$DB_NAME" -f sql/sample_data.sql
    if [ $? -eq 0 ]; then
        echo "✓ Sample data loaded successfully"
    else
        echo "✗ Sample data loading failed"
        exit 1
    fi
fi

# Create views and queries
echo ""
echo "Step 4: Creating views and utility queries..."
psql -U "$DB_USER" -d "$DB_NAME" -f sql/queries.sql
if [ $? -eq 0 ]; then
    echo "✓ Views created successfully"
else
    echo "✗ View creation failed"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Step 5: Creating .env configuration file..."
    read -p "Enter database host (default: localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Enter database port (default: 5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -sp "Enter database password: " DB_PASSWORD
    echo ""
    
    cat > .env << EOF
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF
    echo "✓ .env file created"
else
    echo "⚠ .env file already exists, skipping creation"
fi

echo ""
echo "=========================================="
echo "Database setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Run the application: cd src && python main.py"
echo ""
