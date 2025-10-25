@echo off
echo 🚀 MediTrack - Medicine Adherence Prediction System
echo ==================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed

REM Generate training data if not exists
if not exist "data\training_data.csv" (
    echo 🔬 Generating training data...
    python utils\data_generator.py
    echo ✓ Training data generated
) else (
    echo ✓ Training data already exists
)

REM Create necessary directories
if not exist "uploads" mkdir uploads
if not exist "data" mkdir data
if not exist "static\charts" mkdir static\charts
if not exist "model" mkdir model

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Starting Flask application...
echo 📊 Access the application at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the Flask app
python app.py
