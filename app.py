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

def calculate_medicine_impact(medicines, interaction_checker):
    """
    Calculate the impact of selected medicines on adherence prediction
    
    Factors considered:
    1. Number of medicines (polypharmacy burden)
    2. Drug interactions (complexity and risk)
    3. Medicine characteristics (adherence difficulty)
    """
    score_adjustment = 0
    confidence_adjustment = 0
    recommendations = []
    factors = []
    
    medicine_count = len(medicines)
    
    # 1. Polypharmacy burden
    if medicine_count >= 5:
        score_adjustment -= 8
        confidence_adjustment -= 5
        factors.append(f"High polypharmacy burden ({medicine_count} medicines)")
        recommendations.append(f"⚠️ Managing {medicine_count} medicines is challenging. Consider using a pill organizer.")
    elif medicine_count >= 3:
        score_adjustment -= 4
        confidence_adjustment -= 2
        factors.append(f"Moderate polypharmacy ({medicine_count} medicines)")
    
    # 2. Check for drug interactions
    if medicine_count >= 2:
        # Extract medicine names - handle both string and dict formats
        medicine_names = []
        for med in medicines:
            if isinstance(med, dict):
                medicine_names.append(med.get('name', str(med)))
            else:
                medicine_names.append(str(med))
        
        # Use the check_interactions method which takes a list of medicine names
        interactions = interaction_checker.check_interactions(medicine_names)
        
        interaction_severity = {}
        for interaction in interactions:
            severity = interaction.get('severity', 'unknown')
            interaction_severity[severity] = interaction_severity.get(severity, 0) + 1
        
        interactions_found = len(interactions)
        
        if interactions_found > 0:
            # High severity interactions
            if 'high' in interaction_severity:
                score_adjustment -= interaction_severity['high'] * 6
                confidence_adjustment -= 8
                factors.append(f"{interaction_severity['high']} high-severity drug interactions")
                recommendations.append(f"🚨 {interaction_severity['high']} high-risk drug interactions detected. Consult your doctor immediately.")
            
            # Moderate severity interactions
            if 'moderate' in interaction_severity:
                score_adjustment -= interaction_severity['moderate'] * 3
                confidence_adjustment -= 4
                factors.append(f"{interaction_severity['moderate']} moderate drug interactions")
                recommendations.append(f"⚠️ {interaction_severity['moderate']} moderate drug interactions found. Monitor for side effects.")
            
            # Low severity interactions
            if 'low' in interaction_severity or 'unknown' in interaction_severity:
                low_count = interaction_severity.get('low', 0) + interaction_severity.get('unknown', 0)
                score_adjustment -= low_count * 1
                factors.append(f"{low_count} minor drug interactions")
    
    # 3. Medicine characteristics analysis
    complex_medicines = 0
    high_adherence_medicines = 0
    
    for medicine in medicines:
        # Handle both string and dict formats
        if isinstance(medicine, dict):
            medicine_name = medicine.get('name', str(medicine)).lower()
        else:
            medicine_name = str(medicine).lower()
        
        # Medicines with complex dosing (examples)
        complex_indicators = ['insulin', 'warfarin', 'methotrexate', 'levothyroxine', 'prednisone']
        if any(indicator in medicine_name for indicator in complex_indicators):
            complex_medicines += 1
            score_adjustment -= 3
            factors.append(f"{medicine_name.title()} requires careful dosing")
        
        # Medicines with known adherence issues
        low_adherence_indicators = ['antibiotic', 'antidepressant', 'statin', 'blood pressure']
        if any(indicator in medicine_name for indicator in low_adherence_indicators):
            score_adjustment -= 2
            factors.append(f"{medicine_name.title()} type has lower adherence rates")
        
        # Medicines with typically good adherence
        high_adherence_indicators = ['vitamin', 'supplement', 'aspirin']
        if any(indicator in medicine_name for indicator in high_adherence_indicators):
            high_adherence_medicines += 1
            score_adjustment += 1
    
    if complex_medicines > 0:
        recommendations.append(f"📋 {complex_medicines} of your medicines require careful timing. Set specific reminders for each.")
    
    if high_adherence_medicines > 0:
        confidence_adjustment += 2
        factors.append(f"{high_adherence_medicines} medicines with typically high adherence")
    
    # 4. Overall medicine regimen assessment
    if medicine_count == 0:
        factors.append("No medicines selected for analysis")
        confidence_adjustment -= 10
    elif medicine_count == 1:
        score_adjustment += 5
        confidence_adjustment += 3
        factors.append("Single medicine - easier to manage")
    
    return {
        'score_adjustment': score_adjustment,
        'confidence_adjustment': confidence_adjustment,
        'recommendations': recommendations,
        'factors': factors
    }

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
        medicines = data.get('medicines', [])
        
        # Make base prediction
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
        
        # Apply medicine-specific adjustments
        if medicines:
            medicine_adjustment = calculate_medicine_impact(medicines, drug_checker)
            adjusted_score = prediction['adherence_score'] + medicine_adjustment['score_adjustment']
            adjusted_score = max(0, min(100, adjusted_score))  # Clamp to 0-100
            
            # Recalculate risk level based on adjusted score
            if adjusted_score >= 80:
                risk_level = 'Low'
            elif adjusted_score >= 60:
                risk_level = 'Medium'
            else:
                risk_level = 'High'
            
            # Adjust confidence based on medicine factors
            confidence = prediction['confidence'] + medicine_adjustment['confidence_adjustment']
            confidence = max(50, min(98, confidence))  # Clamp to 50-98
            
            # Add medicine-specific recommendations
            all_recommendations = prediction['recommendations'] + medicine_adjustment['recommendations']
            
            return jsonify({
                'success': True,
                'adherence_score': round(adjusted_score, 2),
                'risk_level': risk_level,
                'recommendations': all_recommendations,
                'confidence': round(confidence, 2),
                'medicine_factors': medicine_adjustment['factors']
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
