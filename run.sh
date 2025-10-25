#!/bin/bash

echo "🚀 MediTrack - Medicine Adherence Prediction System"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Generate training data if not exists
if [ ! -f "data/training_data.csv" ]; then
    echo "🔬 Generating training data..."
    python utils/data_generator.py
    echo "✓ Training data generated"
else
    echo "✓ Training data already exists"
fi

# Create necessary directories
mkdir -p uploads data static/charts model

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting Flask application..."
echo "📊 Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
