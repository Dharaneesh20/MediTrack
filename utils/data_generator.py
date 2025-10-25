import pandas as pd
import numpy as np
import os

def generate_sample_data(num_samples=1000):
    """Generate sample training data for the adherence model"""
    
    np.random.seed(42)
    
    data = []
    
    for _ in range(num_samples):
        # Patient demographics
        age = np.random.randint(18, 85)
        gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.48, 0.48, 0.04])
        
        # Medication details
        medication_count = np.random.randint(1, 8)
        dosage_frequency = np.random.randint(1, 5)
        
        # Behavioral factors
        reminder_enabled = np.random.choice([0, 1], p=[0.3, 0.7])
        missed_doses_last_month = np.random.randint(0, 15)
        
        # Health factors
        comorbidities = np.random.randint(0, 5)
        side_effects = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Socioeconomic factors
        cost_concern = np.random.randint(1, 6)
        
        # Calculate adherence score with realistic correlations
        adherence_score = 90.0
        
        # Age impact
        if age > 70:
            adherence_score -= np.random.uniform(5, 15)
        elif age < 30:
            adherence_score -= np.random.uniform(0, 10)
        
        # Medication complexity
        adherence_score -= medication_count * np.random.uniform(1, 4)
        adherence_score -= dosage_frequency * np.random.uniform(1, 3)
        
        # Behavioral factors
        if reminder_enabled:
            adherence_score += np.random.uniform(10, 20)
        
        adherence_score -= missed_doses_last_month * np.random.uniform(2, 5)
        
        # Health factors
        adherence_score -= comorbidities * np.random.uniform(2, 6)
        if side_effects:
            adherence_score -= np.random.uniform(5, 15)
        
        # Socioeconomic
        adherence_score -= cost_concern * np.random.uniform(1, 4)
        
        # Add some random variation
        adherence_score += np.random.uniform(-5, 5)
        
        # Clip to valid range
        adherence_score = np.clip(adherence_score, 10, 100)
        
        # Binary adherence (>= 80% is adherent)
        adherent = 1 if adherence_score >= 80 else 0
        
        # Encode gender
        gender_encoded = {'Male': 0, 'Female': 1, 'Other': 2}[gender]
        
        data.append({
            'age': age,
            'gender': gender_encoded,
            'medication_count': medication_count,
            'dosage_frequency': dosage_frequency,
            'reminder_enabled': reminder_enabled,
            'missed_doses_last_month': missed_doses_last_month,
            'comorbidities': comorbidities,
            'side_effects': side_effects,
            'cost_concern': cost_concern,
            'adherence_score': round(adherence_score, 2),
            'adherent': adherent
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/training_data.csv', index=False)
    
    print(f"Generated {num_samples} training samples")
    print(f"Adherent patients: {df['adherent'].sum()} ({df['adherent'].mean()*100:.1f}%)")
    print(f"Average adherence score: {df['adherence_score'].mean():.2f}")
    
    return df

if __name__ == '__main__':
    generate_sample_data()
