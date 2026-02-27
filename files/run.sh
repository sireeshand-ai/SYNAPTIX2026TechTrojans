#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Initializing database..."
python database.py

echo ""
echo "Starting the application..."
echo "Open your browser and go to: http://localhost:5000"
python app.py