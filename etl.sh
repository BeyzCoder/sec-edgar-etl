#!/bin/bash

if [ "$1" == "cleanup" ]; then
    echo "Deleting the downloaded resources raw data..."
    rm -rf resources/edgar_companyfacs
    rm -rf resources/edgar_companysubmissions
    rm -f edgar_companyavailable.json
    rm -f edgar_companytickers.json
    rm -f listticker.json
else
    echo "Running extraction script..."
    python script/download_resources.py

    echo "Transforming the raw data into structured format..."
    python script/transform_financials.py

    echo "Loading the structured data into database..."
    docker-compose up --build -d

    echo "Waiting for data load to complete..."
    docker logs -f json_loader | grep -q "All tickers data are in the database!"

    echo "Dumping the data into a .sql file..."
    docker exec -t pgdb pg_dump -U postgres -d companydb > dump.sql
fi 