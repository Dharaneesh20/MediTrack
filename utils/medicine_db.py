import pandas as pd
import os
from difflib import get_close_matches

class MedicineDatabase:
    """
    Handler for medicine dataset with search and information retrieval
    """
    
    def __init__(self, db_path='use_dataset/medicine_dataset.csv'):
        self.db_path = db_path
        self.medicines_db = None
        self.medicine_names = []
        self.load_database()
    
    def load_database(self):
        """Load the medicine database"""
        try:
            if os.path.exists(self.db_path):
                # Read with chunksize due to large file
                chunks = []
                for chunk in pd.read_csv(self.db_path, chunksize=10000, low_memory=False):
                    chunks.append(chunk)
                self.medicines_db = pd.concat(chunks, ignore_index=True)
                
                # Extract medicine names for autocomplete
                self.medicine_names = self.medicines_db['name'].dropna().str.lower().tolist()
                print(f"Loaded {len(self.medicines_db)} medicines from database")
            else:
                print(f"Warning: Medicine database not found at {self.db_path}")
                self.medicines_db = pd.DataFrame()
        except Exception as e:
            print(f"Error loading medicine database: {e}")
            self.medicines_db = pd.DataFrame()
    
    def search_medicine(self, query, limit=10):
        """
        Search for medicines by name
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            list: List of matching medicine names
        """
        if self.medicines_db is None or len(self.medicines_db) == 0:
            return []
        
        query_lower = query.lower().strip()
        
        # Exact and partial matches
        exact_matches = [name for name in self.medicine_names if name.startswith(query_lower)]
        
        # If not enough exact matches, use fuzzy matching
        if len(exact_matches) < limit:
            fuzzy_matches = get_close_matches(query_lower, self.medicine_names, n=limit, cutoff=0.6)
            # Combine and remove duplicates
            matches = list(dict.fromkeys(exact_matches + fuzzy_matches))
        else:
            matches = exact_matches
        
        return matches[:limit]
    
    def get_medicine_info(self, medicine_name):
        """
        Get detailed information about a medicine
        
        Args:
            medicine_name (str): Name of the medicine
            
        Returns:
            dict: Medicine information or None if not found
        """
        if self.medicines_db is None or len(self.medicines_db) == 0:
            return None
        
        medicine_lower = medicine_name.lower().strip()
        
        # Search for the medicine
        medicine_row = self.medicines_db[
            self.medicines_db['name'].str.lower() == medicine_lower
        ]
        
        if medicine_row.empty:
            return None
        
        medicine_data = medicine_row.iloc[0]
        
        # Extract substitutes
        substitutes = []
        for i in range(5):
            sub = medicine_data.get(f'substitute{i}')
            if pd.notna(sub) and sub != '':
                substitutes.append(sub)
        
        # Extract side effects
        side_effects = []
        for i in range(42):
            effect = medicine_data.get(f'sideEffect{i}')
            if pd.notna(effect) and effect != '':
                side_effects.append(effect)
        
        # Extract uses
        uses = []
        for i in range(5):
            use = medicine_data.get(f'use{i}')
            if pd.notna(use) and use != '':
                uses.append(use)
        
        return {
            'id': int(medicine_data.get('id', 0)) if pd.notna(medicine_data.get('id')) else 0,
            'name': medicine_data.get('name', ''),
            'substitutes': substitutes,
            'side_effects': side_effects,
            'uses': uses,
            'chemical_class': medicine_data.get('Chemical Class', 'N/A'),
            'habit_forming': medicine_data.get('Habit Forming', 'No'),
            'therapeutic_class': medicine_data.get('Therapeutic Class', 'N/A'),
            'action_class': medicine_data.get('Action Class', 'N/A')
        }
    
    def get_medicine_side_effects(self, medicine_name):
        """
        Get only side effects for a medicine
        
        Args:
            medicine_name (str): Name of the medicine
            
        Returns:
            list: List of side effects
        """
        info = self.get_medicine_info(medicine_name)
        if info:
            return info['side_effects']
        return []
    
    def get_medicine_substitutes(self, medicine_name):
        """
        Get substitute medicines
        
        Args:
            medicine_name (str): Name of the medicine
            
        Returns:
            list: List of substitute medicines
        """
        info = self.get_medicine_info(medicine_name)
        if info:
            return info['substitutes']
        return []
    
    def batch_search(self, medicine_list):
        """
        Get information for multiple medicines at once
        
        Args:
            medicine_list (list): List of medicine names
            
        Returns:
            dict: Dictionary mapping medicine names to their info
        """
        results = {}
        for medicine in medicine_list:
            info = self.get_medicine_info(medicine)
            if info:
                results[medicine] = info
        return results
    
    def get_medicines_by_therapeutic_class(self, therapeutic_class, limit=20):
        """
        Find medicines by therapeutic class
        
        Args:
            therapeutic_class (str): Therapeutic class name
            limit (int): Maximum results
            
        Returns:
            list: List of medicine names
        """
        if self.medicines_db is None or len(self.medicines_db) == 0:
            return []
        
        matches = self.medicines_db[
            self.medicines_db['Therapeutic Class'].str.contains(
                therapeutic_class, case=False, na=False
            )
        ]
        
        return matches['name'].head(limit).tolist()
    
    def check_habit_forming(self, medicine_name):
        """
        Check if a medicine is habit-forming
        
        Args:
            medicine_name (str): Name of the medicine
            
        Returns:
            bool: True if habit-forming, False otherwise
        """
        info = self.get_medicine_info(medicine_name)
        if info:
            return info['habit_forming'].lower() in ['yes', 'true', '1']
        return False
    
    def get_statistics(self):
        """
        Get database statistics
        
        Returns:
            dict: Statistics about the medicine database
        """
        if self.medicines_db is None or len(self.medicines_db) == 0:
            return {}
        
        return {
            'total_medicines': len(self.medicines_db),
            'therapeutic_classes': self.medicines_db['Therapeutic Class'].nunique(),
            'habit_forming_count': (self.medicines_db['Habit Forming'] == 'Yes').sum(),
            'chemical_classes': self.medicines_db['Chemical Class'].nunique()
        }
