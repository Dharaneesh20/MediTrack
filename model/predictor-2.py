import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
import joblib
import os

class AdherencePredictor:
    """
    Enhanced Adherence Predictor using Ensemble Learning
    
    Algorithm: Voting Regressor (Ensemble)
    - Random Forest Regressor (300 trees)
    - Gradient Boosting Regressor (200 estimators)
    
    The ensemble combines predictions from both models using weighted averaging,
    providing more robust and accurate predictions than single models.
    """
    def __init__(self):
        self.model = None
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model_path = 'model/adherence_model.pkl'
        self.scaler_path = 'model/scaler.pkl'
        self.encoder_path = 'model/encoder.pkl'
        self.feature_importance = None
        self.feature_names = None
        self.uses_gender_dummies = False
        
        # Load model if exists
        if os.path.exists(self.model_path):
            self.load_model()
    
    def prepare_features(self, data):
        """Prepare features for prediction"""
        if self.uses_gender_dummies:
            # Use gender dummies matching training data
            # Map gender to encoding used in training data
            gender_map = {'Male': 0, 'Female': 1, 'Other': 2}
            gender_code = gender_map.get(data['gender'], 2)
            
            features = {
                'age': data['age'],
                'medication_count': data['medication_count'],
                'dosage_frequency': data['dosage_frequency'],
                'reminder_enabled': data['reminder_enabled'],
                'missed_doses_last_month': data['missed_doses_last_month'],
                'comorbidities': data['comorbidities'],
                'side_effects': data['side_effects'],
                'cost_concern': data['cost_concern'],
                'gender_0': 1 if gender_code == 0 else 0,
                'gender_1': 1 if gender_code == 1 else 0,
                'gender_2': 1 if gender_code == 2 else 0
            }
            # Create dataframe with correct column order
            import pandas as pd
            df = pd.DataFrame([features])
            # Reorder columns to match training
            if self.feature_names:
                df = df[self.feature_names]
            return df.values
        else:
            # Simple feature array
            features = []
            
            # Age normalization
            features.append(data['age'] / 100.0)
            
            # Gender encoding
            gender_map = {'Male': 0, 'Female': 1, 'Other': 2}
            features.append(gender_map.get(data['gender'], 2))
            
            # Medication count
            features.append(data['medication_count'])
            
            # Dosage frequency
            features.append(data['dosage_frequency'])
            
            # Reminder enabled
            features.append(data['reminder_enabled'])
            
            # Missed doses
            features.append(data['missed_doses_last_month'])
            
            # Comorbidities
            features.append(data['comorbidities'])
            
            # Side effects
            features.append(data['side_effects'])
            
            # Cost concern
            features.append(data['cost_concern'])
            
            return np.array(features).reshape(1, -1)
    
    def train_model(self, data_path):
        """
        Train the ensemble adherence prediction model
        
        Uses Voting Regressor with:
        1. Random Forest Regressor - Handles non-linear relationships
        2. Gradient Boosting Regressor - Sequential error correction
        """
        # Load data
        df = pd.read_csv(data_path)
        
        # Prepare features
        X = df.drop(['adherence_score', 'adherent'], axis=1)
        y = df['adherence_score']
        
        # Handle categorical variables
        if 'gender' in X.columns:
            gender_dummies = pd.get_dummies(X['gender'], prefix='gender')
            X = pd.concat([X.drop('gender', axis=1), gender_dummies], axis=1)
            self.uses_gender_dummies = True
            self.feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Initialize individual models
        self.rf_model = RandomForestRegressor(
            n_estimators=300,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        self.gb_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42
        )
        
        # Create ensemble model
        self.model = VotingRegressor(
            estimators=[
                ('rf', self.rf_model),
                ('gb', self.gb_model)
            ],
            weights=[1, 1]  # Equal weighting
        )
        
        # Train ensemble
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate feature importance from Random Forest (access fitted estimator)
        rf_estimator = self.model.named_estimators_['rf']
        self.feature_importance = dict(zip(X.columns, rf_estimator.feature_importances_))
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        # Clip predictions to valid range
        y_pred = np.clip(y_pred, 0, 100)
        
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Perform cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, 
                                     cv=5, scoring='r2')
        
        # Calculate classification metrics
        y_test_binary = (y_test >= 70).astype(int)
        y_pred_binary = (y_pred >= 70).astype(int)
        
        accuracy = accuracy_score(y_test_binary, y_pred_binary)
        precision = precision_score(y_test_binary, y_pred_binary, zero_division=0)
        recall = recall_score(y_test_binary, y_pred_binary, zero_division=0)
        f1 = f1_score(y_test_binary, y_pred_binary, zero_division=0)
        
        # Save model
        self.save_model()
        
        return {
            'algorithm': 'Ensemble (Random Forest + Gradient Boosting)',
            'mse': round(mse, 2),
            'r2_score': round(r2, 4),
            'cv_r2_mean': round(cv_scores.mean(), 4),
            'cv_r2_std': round(cv_scores.std(), 4),
            'accuracy': round(accuracy, 4),
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1_score': round(f1, 4),
            'feature_importance': self.feature_importance
        }
    
    def predict(self, patient_data):
        """Predict adherence for a patient"""
        if self.model is None:
            # Use rule-based prediction if model not trained
            return self._rule_based_prediction(patient_data)
        
        # Prepare features
        features = self.prepare_features(patient_data)
        
        # Make prediction
        adherence_score = self.model.predict(features)[0]
        adherence_score = np.clip(adherence_score, 0, 100)
        
        # Determine risk level
        if adherence_score >= 80:
            risk_level = 'Low'
            risk_color = 'success'
        elif adherence_score >= 60:
            risk_level = 'Medium'
            risk_color = 'warning'
        else:
            risk_level = 'High'
            risk_color = 'danger'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(patient_data, adherence_score)
        
        # Calculate confidence (simplified)
        confidence = min(95, 70 + (adherence_score / 5))
        
        return {
            'adherence_score': float(adherence_score),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'recommendations': recommendations,
            'confidence': float(confidence)
        }
    
    def _rule_based_prediction(self, patient_data):
        """Rule-based prediction when ML model is not available"""
        score = 100.0
        
        # Age factor
        if patient_data['age'] > 70:
            score -= 10
        elif patient_data['age'] < 30:
            score -= 5
        
        # Medication complexity
        score -= patient_data['medication_count'] * 3
        score -= patient_data['dosage_frequency'] * 2
        
        # Missed doses impact
        score -= patient_data['missed_doses_last_month'] * 5
        
        # Positive factors
        if patient_data['reminder_enabled']:
            score += 15
        
        # Negative factors
        score -= patient_data['comorbidities'] * 5
        if patient_data['side_effects']:
            score -= 10
        score -= patient_data['cost_concern'] * 5
        
        score = np.clip(score, 0, 100)
        
        # Determine risk level
        if score >= 80:
            risk_level = 'Low'
            risk_color = 'success'
        elif score >= 60:
            risk_level = 'Medium'
            risk_color = 'warning'
        else:
            risk_level = 'High'
            risk_color = 'danger'
        
        recommendations = self._generate_recommendations(patient_data, score)
        
        return {
            'adherence_score': float(score),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'recommendations': recommendations,
            'confidence': 75.0
        }
    
    def _generate_recommendations(self, patient_data, adherence_score):
        """Generate personalized recommendations"""
        recommendations = []
        
        if not patient_data['reminder_enabled']:
            recommendations.append({
                'title': 'Enable Medication Reminders',
                'description': 'Set up daily reminders to improve adherence by 20-30%',
                'priority': 'high'
            })
        
        if patient_data['missed_doses_last_month'] > 5:
            recommendations.append({
                'title': 'Schedule Follow-up Consultation',
                'description': 'Frequent missed doses detected. Consult with healthcare provider.',
                'priority': 'high'
            })
        
        if patient_data['medication_count'] > 5:
            recommendations.append({
                'title': 'Medication Review',
                'description': 'Consider simplifying medication regimen with your doctor',
                'priority': 'medium'
            })
        
        if patient_data['side_effects']:
            recommendations.append({
                'title': 'Discuss Side Effects',
                'description': 'Report side effects to your doctor for possible alternatives',
                'priority': 'high'
            })
        
        if patient_data['cost_concern'] > 3:
            recommendations.append({
                'title': 'Financial Assistance',
                'description': 'Explore generic alternatives or patient assistance programs',
                'priority': 'medium'
            })
        
        if patient_data['dosage_frequency'] > 3:
            recommendations.append({
                'title': 'Simplify Dosage Schedule',
                'description': 'Ask about extended-release formulations for fewer daily doses',
                'priority': 'medium'
            })
        
        if adherence_score < 60:
            recommendations.append({
                'title': 'Adherence Support Program',
                'description': 'Enroll in a medication adherence support program',
                'priority': 'high'
            })
        
        return recommendations
    
    def save_model(self):
        """Save model to disk"""
        os.makedirs('model', exist_ok=True)
        if self.model is not None:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            # Save metadata
            metadata = {
                'uses_gender_dummies': self.uses_gender_dummies,
                'feature_names': self.feature_names,
                'feature_importance': self.feature_importance
            }
            joblib.dump(metadata, 'model/metadata.pkl')
    
    def load_model(self):
        """Load model from disk"""
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            # Load metadata if exists
            if os.path.exists('model/metadata.pkl'):
                metadata = joblib.load('model/metadata.pkl')
                self.uses_gender_dummies = metadata.get('uses_gender_dummies', False)
                self.feature_names = metadata.get('feature_names', None)
                self.feature_importance = metadata.get('feature_importance', None)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
