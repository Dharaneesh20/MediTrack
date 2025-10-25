# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8 or higher installed
- pip package manager

## One-Command Setup (Recommended)

### Linux/macOS:
```bash
./run.sh
```

### Windows:
```cmd
run.bat
```

This script will automatically:
1. Create a virtual environment
2. Install all dependencies
3. Generate training data
4. Start the Flask server

## Manual Setup

If you prefer manual setup:

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate Training Data
```bash
python utils/data_generator.py
```

### 4. Run Application
```bash
python app.py
```

## Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## Quick Tour

1. **Home Page** - Overview of features and SDG alignment
2. **Dashboard** - Real-time statistics and charts
3. **Predict** - Make adherence predictions
4. **Patients** - Manage patient records
5. **Analytics** - Comprehensive insights

## First Prediction

1. Go to **Predict** page
2. Enter patient information:
   - Age: 45
   - Gender: Male
   - Medication Count: 3
   - Dosage Frequency: 2
   - Enable Reminder: Yes
   - Missed Doses: 2
   - Comorbidities: 1
   - Side Effects: No
   - Cost Concern: 3
3. Click **Predict Adherence**
4. View results and recommendations
5. Save patient record

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Training Data Issues
Delete existing data and regenerate:
```bash
rm data/training_data.csv
python utils/data_generator.py
```

## Optional: Tesseract OCR

For full prescription OCR functionality:

### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

### macOS:
```bash
brew install tesseract
```

### Windows:
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## Next Steps

- Explore the Dashboard for analytics
- Add multiple patient records
- Train the model with custom data
- Customize recommendations

## Need Help?

- Check the main README.md for detailed documentation
- Review the API endpoints section
- Open an issue on GitHub

---

**Happy Predicting! 🎯**
