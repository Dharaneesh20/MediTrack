import pandas as pd
import os

class DrugInteractionChecker:
    """
    Checks for drug-drug interactions using the drug interactions database
    """
    
    def __init__(self, db_path='use_dataset/db_drug_interactions.csv'):
        self.db_path = db_path
        self.interactions_db = None
        self.load_database()
    
    def load_database(self):
        """Load the drug interactions database"""
        try:
            if os.path.exists(self.db_path):
                self.interactions_db = pd.read_csv(self.db_path)
                # Normalize drug names to lowercase for better matching
                self.interactions_db['Drug 1'] = self.interactions_db['Drug 1'].str.lower().str.strip()
                self.interactions_db['Drug 2'] = self.interactions_db['Drug 2'].str.lower().str.strip()
                print(f"Loaded {len(self.interactions_db)} drug interactions")
            else:
                print(f"Warning: Database file not found at {self.db_path}")
                self.interactions_db = pd.DataFrame(columns=['Drug 1', 'Drug 2', 'Interaction Description'])
        except Exception as e:
            print(f"Error loading drug interactions database: {e}")
            self.interactions_db = pd.DataFrame(columns=['Drug 1', 'Drug 2', 'Interaction Description'])
    
    def check_interactions(self, medications):
        """
        Check for interactions between a list of medications
        
        Args:
            medications (list): List of medication names
            
        Returns:
            list: List of interaction warnings
        """
        if self.interactions_db is None or len(self.interactions_db) == 0:
            return []
        
        interactions = []
        
        # Normalize medication names
        normalized_meds = [med.lower().strip() for med in medications]
        
        # Check all pairs
        for i in range(len(normalized_meds)):
            for j in range(i + 1, len(normalized_meds)):
                drug1 = normalized_meds[i]
                drug2 = normalized_meds[j]
                
                # Check both directions
                interaction1 = self.interactions_db[
                    (self.interactions_db['Drug 1'] == drug1) & 
                    (self.interactions_db['Drug 2'] == drug2)
                ]
                
                interaction2 = self.interactions_db[
                    (self.interactions_db['Drug 1'] == drug2) & 
                    (self.interactions_db['Drug 2'] == drug1)
                ]
                
                # Add found interactions
                if not interaction1.empty:
                    interactions.append({
                        'drug1': medications[i],
                        'drug2': medications[j],
                        'description': interaction1.iloc[0]['Interaction Description'],
                        'severity': self._classify_severity(interaction1.iloc[0]['Interaction Description'])
                    })
                elif not interaction2.empty:
                    interactions.append({
                        'drug1': medications[i],
                        'drug2': medications[j],
                        'description': interaction2.iloc[0]['Interaction Description'],
                        'severity': self._classify_severity(interaction2.iloc[0]['Interaction Description'])
                    })
        
        return interactions
    
    def _classify_severity(self, description):
        """
        Classify interaction severity based on description keywords
        
        Args:
            description (str): Interaction description
            
        Returns:
            str: Severity level (high, medium, low)
        """
        description_lower = description.lower()
        
        # High severity keywords
        high_keywords = ['severe', 'toxic', 'fatal', 'dangerous', 'contraindicated', 
                        'life-threatening', 'cardiotoxic', 'hepatotoxic', 'nephrotoxic']
        
        # Medium severity keywords
        medium_keywords = ['increased', 'decreased', 'may increase', 'may decrease',
                          'adverse effects', 'side effects', 'risk']
        
        if any(keyword in description_lower for keyword in high_keywords):
            return 'high'
        elif any(keyword in description_lower for keyword in medium_keywords):
            return 'medium'
        else:
            return 'low'
    
    def search_drug(self, drug_name):
        """
        Search for a drug in the interactions database
        
        Args:
            drug_name (str): Name of the drug to search
            
        Returns:
            list: List of all known interactions for this drug
        """
        if self.interactions_db is None or len(self.interactions_db) == 0:
            return []
        
        drug_name_lower = drug_name.lower().strip()
        
        # Find all interactions involving this drug
        interactions = self.interactions_db[
            (self.interactions_db['Drug 1'] == drug_name_lower) | 
            (self.interactions_db['Drug 2'] == drug_name_lower)
        ]
        
        results = []
        for _, row in interactions.iterrows():
            other_drug = row['Drug 2'] if row['Drug 1'] == drug_name_lower else row['Drug 1']
            results.append({
                'interacting_drug': other_drug,
                'description': row['Interaction Description'],
                'severity': self._classify_severity(row['Interaction Description'])
            })
        
        return results
    
    def get_interaction_summary(self, medications):
        """
        Get a summary of all interactions for a list of medications
        
        Args:
            medications (list): List of medication names
            
        Returns:
            dict: Summary with counts by severity
        """
        interactions = self.check_interactions(medications)
        
        summary = {
            'total': len(interactions),
            'high': sum(1 for i in interactions if i['severity'] == 'high'),
            'medium': sum(1 for i in interactions if i['severity'] == 'medium'),
            'low': sum(1 for i in interactions if i['severity'] == 'low'),
            'interactions': interactions
        }
        
        return summary
