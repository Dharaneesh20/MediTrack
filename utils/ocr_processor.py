"""
OCR Utility for Prescription Image Processing
Extracts text from prescription images using Tesseract OCR
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
import os

class PrescriptionOCR:
    def __init__(self):
        # Configure tesseract path if needed (adjust for your system)
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        
        # Common medicine prefixes and suffixes
        self.medicine_patterns = [
            r'\b([A-Z][a-z]{2,}(?:in|ol|ate|ide|ine|cin|lol|pril|pine|zole|mycin|cillin))\b',  # Common endings
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+\d+\s*(?:mg|ml|g|mcg|tablet|tab|cap|capsule)s?\b',  # With dosage
            r'(?:Rx|Medication|Medicine|Drug|Tab|Cap)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',  # After Rx/Med labels
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+-\s+\d+',  # Name - dosage format
        ]
    
    def extract_text(self, image_path):
        """
        Extract text from prescription image with preprocessing
        
        Args:
            image_path (str): Path to the prescription image
            
        Returns:
            dict: Extracted text and processing status
        """
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Try multiple OCR configurations
            raw_text = self._extract_with_multiple_configs(processed_image)
            
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
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to grayscale
            image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            return image
        except Exception as e:
            # Return original image if preprocessing fails
            return image
    
    def _extract_with_multiple_configs(self, image):
        """Try multiple OCR configurations for best results"""
        configs = [
            '--psm 6',  # Assume uniform block of text
            '--psm 4',  # Assume single column of text
            '--psm 3',  # Fully automatic page segmentation
        ]
        
        best_text = ""
        max_confidence = 0
        
        for config in configs:
            try:
                # Extract with English only first
                text = pytesseract.image_to_string(image, lang='eng', config=config)
                
                # Basic quality check - count alphabetic characters
                alpha_count = sum(c.isalpha() for c in text)
                
                if alpha_count > max_confidence:
                    max_confidence = alpha_count
                    best_text = text
            except:
                continue
        
        return best_text if best_text else pytesseract.image_to_string(image, lang='eng')
    
    def _clean_text(self, text):
        """Clean and format extracted text aggressively"""
        if not text:
            return ""
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove lines with too many non-alphabetic characters (likely garbage)
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Calculate ratio of alphabetic characters
            alpha_count = sum(c.isalpha() for c in line)
            total_count = len(line)
            
            # Keep lines with at least 40% alphabetic characters
            if total_count > 0 and (alpha_count / total_count) >= 0.4:
                clean_lines.append(line)
        
        text = ' '.join(clean_lines)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\,\:\-\(\)\+]', '', text)
        
        # Fix common OCR errors
        text = self._fix_common_ocr_errors(text)
        
        # Capitalize sentences properly
        sentences = text.split('.')
        sentences = [s.strip().capitalize() for s in sentences if s.strip()]
        
        return '. '.join(sentences)
    
    def _fix_common_ocr_errors(self, text):
        """Fix common OCR misreads"""
        # Common substitutions
        replacements = {
            r'\b0(?=[a-zA-Z])': 'O',  # 0 before letter -> O
            r'(?<=[a-zA-Z])0\b': 'O',  # 0 after letter -> O
            r'\bl(?=[A-Z])': 'I',  # lowercase l before capital -> I
            r'\b1(?=[a-zA-Z]{2,})': 'I',  # 1 before word -> I
            r'rn': 'm',  # Common misread
            r'\|': 'I',  # Pipe to I
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _extract_medicines(self, text):
        """
        Try to extract medicine names from text using multiple patterns
        """
        medicines = set()
        
        # Apply all medicine patterns
        for pattern in self.medicine_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean the match
                medicine = match.strip() if isinstance(match, str) else match[0].strip()
                
                # Filter out common false positives
                if self._is_valid_medicine_name(medicine):
                    medicines.add(medicine.title())
        
        # Additional pattern: Look for lines with specific keywords
        lines = text.split('.')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['tablet', 'capsule', 'syrup', 'injection', 'mg', 'ml']):
                # Extract capitalized words before numbers
                words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', line)
                for word in words:
                    if self._is_valid_medicine_name(word):
                        medicines.add(word.title())
        
        return sorted(list(medicines))
    
    def _is_valid_medicine_name(self, name):
        """Validate if extracted text is likely a medicine name"""
        if not name or len(name) < 3:
            return False
        
        # Remove common false positives
        false_positives = {
            'the', 'and', 'for', 'with', 'from', 'this', 'that',
            'prescription', 'doctor', 'patient', 'name', 'date',
            'address', 'phone', 'email', 'tablet', 'capsule', 'mg', 'ml'
        }
        
        if name.lower() in false_positives:
            return False
        
        # Must contain mostly alphabetic characters
        alpha_count = sum(c.isalpha() for c in name)
        if alpha_count < len(name) * 0.7:
            return False
        
        # Should have at least one vowel
        if not any(v in name.lower() for v in 'aeiou'):
            return False
        
        return True
    
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
            result['suggestions'] = self._get_suggestions(result['cleaned_text'], result['raw_text'])
            
            # Add quality indicator
            result['quality'] = self._assess_quality(result['raw_text'])
        
        return result
    
    def _assess_quality(self, text):
        """Assess OCR quality"""
        if not text:
            return "poor"
        
        # Calculate quality metrics
        alpha_ratio = sum(c.isalpha() for c in text) / len(text) if len(text) > 0 else 0
        space_ratio = sum(c.isspace() for c in text) / len(text) if len(text) > 0 else 0
        
        if alpha_ratio > 0.6 and space_ratio < 0.3:
            return "good"
        elif alpha_ratio > 0.4:
            return "moderate"
        else:
            return "poor"
    
    def _get_suggestions(self, cleaned_text, raw_text):
        """Provide suggestions for common OCR errors and quality issues"""
        suggestions = []
        
        # Check OCR quality
        quality = self._assess_quality(raw_text)
        
        if quality == "poor":
            suggestions.append("⚠️ Poor image quality detected. Try uploading a clearer image.")
            suggestions.append("💡 Ensure good lighting and focus when capturing prescription.")
        elif quality == "moderate":
            suggestions.append("⚠️ Some text may be unclear. Please review carefully.")
        
        # Check for common OCR misreads
        common_errors = {
            '0': 'O (letter O)',
            '1': 'I or l',
            '5': 'S',
            '8': 'B',
            'rn': 'm',
        }
        
        for error, correction in common_errors.items():
            if error in cleaned_text:
                suggestions.append(f"Check if '{error}' should be '{correction}'")
        
        # Check if text is too short
        if len(cleaned_text) < 20:
            suggestions.append("⚠️ Very little text extracted. Image may need adjustment.")
        
        # Check if no medicines found
        if not cleaned_text or len(cleaned_text.strip()) < 10:
            suggestions.append("❌ Unable to extract meaningful text. Please try:")
            suggestions.append("  • Taking photo in better lighting")
            suggestions.append("  • Ensuring prescription is clearly visible")
            suggestions.append("  • Using a higher resolution image")
        
        return suggestions if suggestions else ["✅ Text extraction looks good! Review and edit as needed."]
