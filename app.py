from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime, timedelta
import numpy as np
from werkzeug.utils import secure_filename
from model.predictor import AdherencePredictor
from utils.prescription_reader import PrescriptionReader
from utils.data_generator import generate_sample_data
from utils.drug_interaction_checker import DrugInteractionChecker
from utils.medicine_db import MedicineDatabase
from utils.ocr_processor import PrescriptionOCR

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}

# Initialize ML model and utilities
predictor = AdherencePredictor()
prescription_reader = PrescriptionReader()
drug_checker = DrugInteractionChecker()
medicine_db = MedicineDatabase()
ocr_processor = PrescriptionOCR()

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/charts', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/patients')
def patients_page():
    return render_template('patients.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/api/predict', methods=['POST'])
def predict_adherence():
    try:
        data = request.json
        
        # Extract features
        age = int(data.get('age', 0))
        gender = data.get('gender', 'Other')
        medication_count = int(data.get('medication_count', 1))
        dosage_frequency = int(data.get('dosage_frequency', 1))
        reminder_enabled = 1 if data.get('reminder_enabled') else 0
        missed_doses_last_month = int(data.get('missed_doses_last_month', 0))
        comorbidities = int(data.get('comorbidities', 0))
        side_effects = 1 if data.get('side_effects') else 0
        cost_concern = int(data.get('cost_concern', 1))
        
        # Make prediction
        prediction = predictor.predict({
            'age': age,
            'gender': gender,
            'medication_count': medication_count,
            'dosage_frequency': dosage_frequency,
            'reminder_enabled': reminder_enabled,
            'missed_doses_last_month': missed_doses_last_month,
            'comorbidities': comorbidities,
            'side_effects': side_effects,
            'cost_concern': cost_concern
        })
        
        return jsonify({
            'success': True,
            'adherence_score': round(prediction['adherence_score'], 2),
            'risk_level': prediction['risk_level'],
            'recommendations': prediction['recommendations'],
            'confidence': round(prediction['confidence'], 2)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/upload_prescription', methods=['POST'])
def upload_prescription():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract prescription data
            prescription_data = prescription_reader.extract_data(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'data': prescription_data
            })
        
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/patients', methods=['GET', 'POST'])
def manage_patients():
    patients_file = 'data/patients.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(patients_file):
                with open(patients_file, 'r') as f:
                    patients = json.load(f)
            else:
                patients = []
            return jsonify({'success': True, 'patients': patients})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'POST':
        try:
            patient_data = request.json
            patient_data['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
            patient_data['created_at'] = datetime.now().isoformat()
            
            patients = []
            if os.path.exists(patients_file):
                with open(patients_file, 'r') as f:
                    patients = json.load(f)
            
            patients.append(patient_data)
            
            with open(patients_file, 'w') as f:
                json.dump(patients, f, indent=2)
            
            return jsonify({'success': True, 'patient': patient_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    try:
        patients_file = 'data/patients.json'
        patients = []
        
        if os.path.exists(patients_file):
            with open(patients_file, 'r') as f:
                patients = json.load(f)
        
        # Calculate analytics
        total_patients = len(patients)
        high_risk = sum(1 for p in patients if p.get('risk_level') == 'High')
        medium_risk = sum(1 for p in patients if p.get('risk_level') == 'Medium')
        low_risk = sum(1 for p in patients if p.get('risk_level') == 'Low')
        
        avg_adherence = np.mean([p.get('adherence_score', 0) for p in patients]) if patients else 0
        
        return jsonify({
            'success': True,
            'total_patients': total_patients,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk,
            'average_adherence': round(avg_adherence, 2),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/reminders', methods=['GET', 'POST'])
def manage_reminders():
    reminders_file = 'data/reminders.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(reminders_file):
                with open(reminders_file, 'r') as f:
                    reminders = json.load(f)
            else:
                reminders = []
            return jsonify({'success': True, 'reminders': reminders})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    elif request.method == 'POST':
        try:
            reminder_data = request.json
            reminder_data['id'] = datetime.now().strftime('%Y%m%d%H%M%S')
            reminder_data['created_at'] = datetime.now().isoformat()
            
            reminders = []
            if os.path.exists(reminders_file):
                with open(reminders_file, 'r') as f:
                    reminders = json.load(f)
            
            reminders.append(reminder_data)
            
            with open(reminders_file, 'w') as f:
                json.dump(reminders, f, indent=2)
            
            return jsonify({'success': True, 'reminder': reminder_data})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/train_model', methods=['POST'])
def train_model():
    try:
        # Generate sample data if not exists
        if not os.path.exists('data/training_data.csv'):
            generate_sample_data()
        
        # Train the model
        metrics = predictor.train_model('data/training_data.csv')
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'message': 'Model trained successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/search_medicine', methods=['GET'])
def search_medicine():
    """Search for medicines by name"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        if not query or len(query) < 2:
            return jsonify({'success': True, 'results': []})
        
        results = medicine_db.search_medicine(query, limit)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/medicine_info/<medicine_name>', methods=['GET'])
def get_medicine_info(medicine_name):
    """Get detailed information about a medicine"""
    try:
        info = medicine_db.get_medicine_info(medicine_name)
        
        if info:
            return jsonify({
                'success': True,
                'medicine': info
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Medicine not found'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/check_interactions', methods=['POST'])
def check_drug_interactions():
    """Check for drug-drug interactions"""
    try:
        data = request.json
        medications = data.get('medications', [])
        
        if not medications or len(medications) < 2:
            return jsonify({
                'success': True,
                'summary': {
                    'total': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'interactions': []
                }
            })
        
        summary = drug_checker.get_interaction_summary(medications)
        
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/medicine_batch', methods=['POST'])
def get_medicine_batch():
    """Get information for multiple medicines"""
    try:
        data = request.json
        medicines = data.get('medicines', [])
        
        results = medicine_db.batch_search(medicines)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/medicine_stats', methods=['GET'])
def get_medicine_stats():
    """Get database statistics"""
    try:
        stats = medicine_db.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/ocr/extract', methods=['POST'])
def extract_prescription_text():
    """Extract text from prescription image using OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only PNG, JPG, JPEG allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process with OCR
        result = ocr_processor.process_prescription(filepath)
        
        # Clean up file after processing (optional - comment out if you want to keep files)
        # os.remove(filepath)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Generate sample data if not exists
    if not os.path.exists('data/training_data.csv'):
        print("Generating sample training data...")
        generate_sample_data()
        print("Training initial model...")
        predictor.train_model('data/training_data.csv')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
