#!/bin/bash

set -e  # exit on error

# Get directory of this script, no matter where it's run from
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ "$1" == "cleanup" ]; then
    echo "Deleting the downloaded resources raw data..."
    rm -rf resources/edgar_companyfacts
    rm -rf resources/edgar_companysubmissions
    rm -f resources/edgar_companyavailable.json
    rm -f resources/edgar_companytickers.json
    rm -f resources/listticker.json
    docker-compose down -v --rmi all --remove-orphans
else
    echo "Running extraction script..."
    python scripts/download_resources.py

    echo "Transforming the raw data into structured format..."
    python scripts/transform_financials.py

    echo "Loading the structured data into database..."
    docker-compose up --build -d

    echo "Waiting for data load to complete..."
    docker logs -f json_loader 2>&1 | tee /dev/stderr | grep -m 1 "All tickers data are in the database!"

    echo "Dumping the data into a .sql file..."
    docker exec -t pgdb pg_dump -U postgres -d companydb > dump.sql
fi 