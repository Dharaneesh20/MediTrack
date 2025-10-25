"""
OCR Utility for Prescription Image Processing
Extracts text from prescription images using Tesseract OCR
"""

import pytesseract
from PIL import Image
import re
import os

class PrescriptionOCR:
    def __init__(self):
        # Configure tesseract path if needed (adjust for your system)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        pass
    
    def extract_text(self, image_path):
        """
        Extract text from prescription image
        
        Args:
            image_path (str): Path to the prescription image
            
        Returns:
            dict: Extracted text and processing status
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Perform OCR
            raw_text = pytesseract.image_to_string(image, lang='eng')
            
            # Clean and process text
            cleaned_text = self._clean_text(raw_text)
            
            # Extract medicines if possible
            medicines = self._extract_medicines(cleaned_text)
            
            return {
                'success': True,
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'medicines': medicines
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_text': '',
                'cleaned_text': '',
                'medicines': []
            }
    
    def _clean_text(self, text):
        """Clean and format extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\,\:\-\(\)]', '', text)
        
        # Capitalize properly
        lines = text.split('.')
        lines = [line.strip().capitalize() for line in lines if line.strip()]
        
        return '. '.join(lines)
    
    def _extract_medicines(self, text):
        """
        Try to extract medicine names from text
        Common patterns: medicine name followed by dosage
        """
        medicines = []
        
        # Common medicine name patterns
        # Look for capitalized words followed by numbers (dosage)
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d+\s*(?:mg|ml|tablet|capsule|tab)'
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        medicines.extend(matches)
        
        # Look for lines starting with "Rx:" or "Medicine:"
        rx_pattern = r'(?:Rx|Medicine|Drug)[\s:]+([A-Za-z\s]+?)(?:\d+|$|\n)'
        rx_matches = re.findall(rx_pattern, text, re.IGNORECASE)
        medicines.extend([m.strip() for m in rx_matches])
        
        # Remove duplicates and clean
        medicines = list(set([m.strip() for m in medicines if len(m.strip()) > 2]))
        
        return medicines
    
    def process_prescription(self, image_path):
        """
        Complete prescription processing pipeline
        
        Args:
            image_path (str): Path to prescription image
            
        Returns:
            dict: Comprehensive extraction results
        """
        result = self.extract_text(image_path)
        
        if result['success']:
            # Add additional processing here
            result['editable_text'] = result['cleaned_text']
            result['suggestions'] = self._get_suggestions(result['cleaned_text'])
        
        return result
    
    def _get_suggestions(self, text):
        """Provide suggestions for common OCR errors"""
        suggestions = []
        
        # Check for common OCR misreads
        common_errors = {
            '0': 'O',
            '1': 'I or l',
            '5': 'S',
            '8': 'B',
        }
        
        for digit, letter in common_errors.items():
            if digit in text:
                suggestions.append(f"Check if '{digit}' should be '{letter}'")
        
        return suggestions
