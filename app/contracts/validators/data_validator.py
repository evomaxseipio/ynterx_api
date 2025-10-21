from typing import Dict, Any, List, Union
import re


class DataValidator:
    """Validador de datos general"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validar formato de teléfono"""
        if not phone:
            return False
        
        # Remover espacios, guiones y paréntesis
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Validar que solo contenga números y tenga longitud razonable
        return clean_phone.isdigit() and 7 <= len(clean_phone) <= 15
    
    @staticmethod
    def validate_document_number(document_number: str, document_type: str = None) -> bool:
        """Validar número de documento"""
        if not document_number:
            return False
        
        # Validaciones específicas por tipo de documento
        if document_type == "Cédula":
            # Cédula dominicana: 11 dígitos
            return document_number.isdigit() and len(document_number) == 11
        elif document_type == "Pasaporte":
            # Pasaporte: alfanumérico, 6-9 caracteres
            return bool(re.match(r'^[A-Z0-9]{6,9}$', document_number.upper()))
        else:
            # Validación general: alfanumérico, 5-20 caracteres
            return bool(re.match(r'^[A-Z0-9\-]{5,20}$', document_number.upper()))
    
    @staticmethod
    def validate_amount(amount: Union[int, float]) -> bool:
        """Validar monto"""
        if amount is None:
            return False
        
        try:
            amount_float = float(amount)
            return amount_float > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_percentage(percentage: Union[int, float]) -> bool:
        """Validar porcentaje"""
        if percentage is None:
            return False
        
        try:
            percentage_float = float(percentage)
            return 0 <= percentage_float <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_format(date_str: str, format_pattern: str = None) -> bool:
        """Validar formato de fecha"""
        if not date_str:
            return False
        
        try:
            from datetime import datetime
            
            if format_pattern:
                datetime.strptime(date_str, format_pattern)
            else:
                # Intentar formatos comunes
                formats = [
                    "%Y-%m-%d",
                    "%d/%m/%Y",
                    "%m/%d/%Y",
                    "%d-%m-%Y",
                    "%Y/%m/%d"
                ]
                
                for fmt in formats:
                    try:
                        datetime.strptime(date_str, fmt)
                        return True
                    except ValueError:
                        continue
                
                return False
        except ValueError:
            return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validar campos requeridos"""
        errors = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                errors.append(f"Campo '{field}' es requerido")
        
        return errors
    
    @staticmethod
    def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> List[str]:
        """Validar tipos de campos"""
        errors = []
        
        for field, expected_type in field_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Campo '{field}' debe ser de tipo {expected_type.__name__}")
        
        return errors
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = None) -> bool:
        """Validar longitud de string"""
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length:
            return False
        
        if max_length and len(value) > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_value: Union[int, float] = None, max_value: Union[int, float] = None) -> bool:
        """Validar rango numérico"""
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
