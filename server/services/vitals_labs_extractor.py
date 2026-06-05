"""
Vitals and Lab Values Extractor
Extracts numerical health measurements from medical reports
"""

import re
from typing import Dict, List, Any

class VitalsLabsExtractor:
    """Extract vital signs and laboratory values from medical text"""
    
    def __init__(self):
        # Normal ranges for common measurements
        self.normal_ranges = {
            # Vitals
            'blood_pressure_systolic': (90, 120),
            'blood_pressure_diastolic': (60, 80),
            'heart_rate': (60, 100),
            'temperature_f': (97.0, 99.0),
            'temperature_c': (36.1, 37.2),
            'respiratory_rate': (12, 20),
            'oxygen_saturation': (95, 100),
            'weight_kg': (40, 200),  # Broad range
            'bmi': (18.5, 24.9),
            
            # Lab values
            'glucose': (70, 100),  # mg/dL fasting
            'hba1c': (4.0, 5.6),  # %
            'cholesterol_total': (0, 200),  # mg/dL
            'cholesterol_ldl': (0, 100),  # mg/dL
            'cholesterol_hdl': (40, 200),  # mg/dL
            'triglycerides': (0, 150),  # mg/dL
            'creatinine': (0.7, 1.3),  # mg/dL
            'bun': (7, 20),  # mg/dL
            'alt': (7, 56),  # U/L
            'ast': (10, 40),  # U/L
            'hemoglobin': (12.0, 17.0),  # g/dL
            'wbc': (4.0, 11.0),  # 10^3/μL
            'platelets': (150, 400),  # 10^3/μL
        }
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all vitals and lab values from text
        
        Args:
            text: Medical report text
            
        Returns:
            Dictionary with vitals and labs
        """
        text_lower = text.lower()
        
        vitals = self._extract_vitals(text_lower)
        labs = self._extract_labs(text_lower)
        
        return {
            'vitals': vitals,
            'labs': labs
        }
    
    def _extract_vitals(self, text: str) -> Dict[str, Any]:
        """Extract vital signs from text"""
        vitals = {}
        
        # Blood Pressure (various formats)
        bp_patterns = [
            r'blood pressure[:\s]+(\d{2,3})[/\\](\d{2,3})',
            r'bp[:\s]+(\d{2,3})[/\\](\d{2,3})',
            r'(\d{2,3})[/\\](\d{2,3})\s*mmhg',
        ]
        for pattern in bp_patterns:
            match = re.search(pattern, text)
            if match:
                systolic = int(match.group(1))
                diastolic = int(match.group(2))
                vitals['blood_pressure'] = f"{systolic}/{diastolic}"
                vitals['blood_pressure_systolic'] = systolic
                vitals['blood_pressure_diastolic'] = diastolic
                break
        
        # Heart Rate
        hr_patterns = [
            r'heart rate[:\s]+(\d{2,3})',
            r'hr[:\s]+(\d{2,3})',
            r'pulse[:\s]+(\d{2,3})',
            r'(\d{2,3})\s*bpm',
        ]
        for pattern in hr_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['heart_rate'] = int(match.group(1))
                break
        
        # Temperature
        temp_patterns = [
            r'temperature[:\s]+(\d{2,3}\.?\d*)\s*°?f',
            r'temp[:\s]+(\d{2,3}\.?\d*)\s*°?f',
            r'(\d{2,3}\.?\d*)\s*°f',
        ]
        for pattern in temp_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['temperature_f'] = float(match.group(1))
                break
        
        # Temperature Celsius
        temp_c_patterns = [
            r'temperature[:\s]+(\d{2}\.?\d*)\s*°?c',
            r'temp[:\s]+(\d{2}\.?\d*)\s*°?c',
            r'(\d{2}\.?\d*)\s*°c',
        ]
        for pattern in temp_c_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['temperature_c'] = float(match.group(1))
                break
        
        # Respiratory Rate
        rr_patterns = [
            r'respiratory rate[:\s]+(\d{1,2})',
            r'rr[:\s]+(\d{1,2})',
            r'respiration[:\s]+(\d{1,2})',
        ]
        for pattern in rr_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['respiratory_rate'] = int(match.group(1))
                break
        
        # Oxygen Saturation
        o2_patterns = [
            r'oxygen saturation[:\s]+(\d{2,3})',
            r'spo2[:\s]+(\d{2,3})',
            r'o2 sat[:\s]+(\d{2,3})',
            r'(\d{2,3})%\s*o2',
        ]
        for pattern in o2_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['oxygen_saturation'] = int(match.group(1))
                break
        
        # Weight
        weight_patterns = [
            r'weight[:\s]+(\d{2,3}\.?\d*)\s*kg',
            r'(\d{2,3}\.?\d*)\s*kilograms',
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['weight_kg'] = float(match.group(1))
                break
        
        # BMI
        bmi_patterns = [
            r'bmi[:\s]+(\d{1,2}\.?\d*)',
            r'body mass index[:\s]+(\d{1,2}\.?\d*)',
        ]
        for pattern in bmi_patterns:
            match = re.search(pattern, text)
            if match:
                vitals['bmi'] = float(match.group(1))
                break
        
        return vitals
    
    def _extract_labs(self, text: str) -> Dict[str, Any]:
        """Extract laboratory values from text"""
        labs = {}
        
        # Glucose / Blood Sugar
        glucose_patterns = [
            r'glucose[:\s]+(\d{2,3})',
            r'blood sugar[:\s]+(\d{2,3})',
            r'fasting glucose[:\s]+(\d{2,3})',
            r'fbs[:\s]+(\d{2,3})',
        ]
        for pattern in glucose_patterns:
            match = re.search(pattern, text)
            if match:
                labs['glucose'] = int(match.group(1))
                break
        
        # HbA1c
        hba1c_patterns = [
            r'hba1c[:\s]+(\d{1,2}\.?\d*)',
            r'a1c[:\s]+(\d{1,2}\.?\d*)',
            r'glycated hemoglobin[:\s]+(\d{1,2}\.?\d*)',
        ]
        for pattern in hba1c_patterns:
            match = re.search(pattern, text)
            if match:
                labs['hba1c'] = float(match.group(1))
                break
        
        # Cholesterol - Total
        chol_total_patterns = [
            r'total cholesterol[:\s]+(\d{2,3})',
            r'cholesterol[:\s]+(\d{2,3})',
        ]
        for pattern in chol_total_patterns:
            match = re.search(pattern, text)
            if match:
                labs['cholesterol_total'] = int(match.group(1))
                break
        
        # LDL Cholesterol
        ldl_patterns = [
            r'ldl cholesterol[:\s]+(\d{2,3})',
            r'ldl[:\s]+(\d{2,3})',
            r'low density lipoprotein[:\s]+(\d{2,3})',
        ]
        for pattern in ldl_patterns:
            match = re.search(pattern, text)
            if match:
                labs['cholesterol_ldl'] = int(match.group(1))
                break
        
        # HDL Cholesterol
        hdl_patterns = [
            r'hdl cholesterol[:\s]+(\d{2,3})',
            r'hdl[:\s]+(\d{2,3})',
            r'high density lipoprotein[:\s]+(\d{2,3})',
        ]
        for pattern in hdl_patterns:
            match = re.search(pattern, text)
            if match:
                labs['cholesterol_hdl'] = int(match.group(1))
                break
        
        # Triglycerides
        trig_patterns = [
            r'triglycerides[:\s]+(\d{2,3})',
            r'tg[:\s]+(\d{2,3})',
        ]
        for pattern in trig_patterns:
            match = re.search(pattern, text)
            if match:
                labs['triglycerides'] = int(match.group(1))
                break
        
        # Creatinine
        creat_patterns = [
            r'creatinine[:\s]+(\d{1}\.\d{1,2})',
            r'cr[:\s]+(\d{1}\.\d{1,2})',
        ]
        for pattern in creat_patterns:
            match = re.search(pattern, text)
            if match:
                labs['creatinine'] = float(match.group(1))
                break
        
        # BUN (Blood Urea Nitrogen)
        bun_patterns = [
            r'bun[:\s]+(\d{1,2})',
            r'blood urea nitrogen[:\s]+(\d{1,2})',
        ]
        for pattern in bun_patterns:
            match = re.search(pattern, text)
            if match:
                labs['bun'] = int(match.group(1))
                break
        
        # ALT (Liver enzyme)
        alt_patterns = [
            r'alt[:\s]+(\d{1,3})',
            r'alanine aminotransferase[:\s]+(\d{1,3})',
            r'sgpt[:\s]+(\d{1,3})',
        ]
        for pattern in alt_patterns:
            match = re.search(pattern, text)
            if match:
                labs['alt'] = int(match.group(1))
                break
        
        # AST (Liver enzyme)
        ast_patterns = [
            r'ast[:\s]+(\d{1,3})',
            r'aspartate aminotransferase[:\s]+(\d{1,3})',
            r'sgot[:\s]+(\d{1,3})',
        ]
        for pattern in ast_patterns:
            match = re.search(pattern, text)
            if match:
                labs['ast'] = int(match.group(1))
                break
        
        # Hemoglobin
        hgb_patterns = [
            r'hemoglobin[:\s]+(\d{1,2}\.?\d*)',
            r'hgb[:\s]+(\d{1,2}\.?\d*)',
            r'hb[:\s]+(\d{1,2}\.?\d*)',
        ]
        for pattern in hgb_patterns:
            match = re.search(pattern, text)
            if match:
                labs['hemoglobin'] = float(match.group(1))
                break
        
        # WBC (White Blood Cells)
        wbc_patterns = [
            r'wbc[:\s]+(\d{1,2}\.?\d*)',
            r'white blood cell[:\s]+(\d{1,2}\.?\d*)',
            r'leukocytes[:\s]+(\d{1,2}\.?\d*)',
        ]
        for pattern in wbc_patterns:
            match = re.search(pattern, text)
            if match:
                labs['wbc'] = float(match.group(1))
                break
        
        # Platelets
        plt_patterns = [
            r'platelets[:\s]+(\d{2,3})',
            r'plt[:\s]+(\d{2,3})',
        ]
        for pattern in plt_patterns:
            match = re.search(pattern, text)
            if match:
                labs['platelets'] = int(match.group(1))
                break
        
        return labs
    
    def check_abnormal_values(self, vitals: Dict, labs: Dict) -> List[Dict]:
        """
        Check for abnormal values in vitals and labs
        
        Args:
            vitals: Dictionary of vital signs
            labs: Dictionary of lab values
            
        Returns:
            List of warnings for abnormal values
        """
        warnings = []
        
        # Check vitals
        for key, value in vitals.items():
            if key in self.normal_ranges:
                min_val, max_val = self.normal_ranges[key]
                
                if value < min_val:
                    warnings.append({
                        'type': 'vital',
                        'name': self._format_name(key),
                        'value': value,
                        'normal_range': f"{min_val}-{max_val}",
                        'status': 'below_normal',
                        'level': self._get_severity_level(key, value, min_val, max_val)
                    })
                elif value > max_val:
                    warnings.append({
                        'type': 'vital',
                        'name': self._format_name(key),
                        'value': value,
                        'normal_range': f"{min_val}-{max_val}",
                        'status': 'above_normal',
                        'level': self._get_severity_level(key, value, min_val, max_val)
                    })
        
        # Check labs
        for key, value in labs.items():
            if key in self.normal_ranges:
                min_val, max_val = self.normal_ranges[key]
                
                if value < min_val:
                    warnings.append({
                        'type': 'lab',
                        'name': self._format_name(key),
                        'value': value,
                        'normal_range': f"{min_val}-{max_val}",
                        'status': 'below_normal',
                        'level': self._get_severity_level(key, value, min_val, max_val)
                    })
                elif value > max_val:
                    warnings.append({
                        'type': 'lab',
                        'name': self._format_name(key),
                        'value': value,
                        'normal_range': f"{min_val}-{max_val}",
                        'status': 'above_normal',
                        'level': self._get_severity_level(key, value, min_val, max_val)
                    })
        
        return warnings
    
    def _format_name(self, key: str) -> str:
        """Format technical name to readable format"""
        formatted = key.replace('_', ' ').title()
        
        # Special cases
        replacements = {
            'Bmi': 'BMI',
            'Wbc': 'WBC (White Blood Cells)',
            'Hdl': 'HDL Cholesterol',
            'Ldl': 'LDL Cholesterol',
            'Alt': 'ALT (Liver Enzyme)',
            'Ast': 'AST (Liver Enzyme)',
            'Bun': 'BUN (Blood Urea Nitrogen)',
            'Hba1C': 'HbA1c',
        }
        
        for old, new in replacements.items():
            formatted = formatted.replace(old, new)
        
        return formatted
    
    def _get_severity_level(self, key: str, value: float, min_val: float, max_val: float) -> str:
        """
        Determine severity level of abnormal value
        
        Returns:
            'urgent', 'concern', or 'mild'
        """
        # Calculate how far outside normal range
        if value < min_val:
            deviation = (min_val - value) / min_val
        else:
            deviation = (value - max_val) / max_val
        
        # Critical thresholds for specific measurements
        urgent_conditions = {
            'blood_pressure_systolic': lambda v: v > 180 or v < 90,
            'blood_pressure_diastolic': lambda v: v > 120 or v < 60,
            'glucose': lambda v: v > 300 or v < 50,
            'oxygen_saturation': lambda v: v < 90,
            'temperature_f': lambda v: v > 103 or v < 95,
        }
        
        if key in urgent_conditions and urgent_conditions[key](value):
            return 'urgent'
        
        # General severity based on deviation
        if deviation > 0.5:  # >50% outside range
            return 'urgent'
        elif deviation > 0.25:  # >25% outside range
            return 'concern'
        else:
            return 'mild'


# Global instance
vitals_labs_extractor = VitalsLabsExtractor()