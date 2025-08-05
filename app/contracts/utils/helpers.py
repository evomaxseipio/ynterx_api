# utils.py
from typing import Any, Dict

def clean_data_for_template(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recorre el dict y limpia caracteres conflictivos para docx"""
    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean(item) for item in value]
        elif isinstance(value, str):
            return value.replace('\r\n', '\n').replace('\r', '\n')
        return value
    return clean(data)

def is_mortgage_data(data: Dict[str, Any]) -> bool:
    mortgage_indicators = ['loan', 'properties', 'clients', 'investors', 'witnesses', 'notaries']
    return sum(1 for key in mortgage_indicators if key in data) >= 4
