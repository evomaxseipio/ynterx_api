#!/usr/bin/env python3
"""
Debug script to identify the exact issue with the JSON validation.
"""

import json
from typing import Dict, Any

from app.person.schemas import PersonCompleteCreate


def simulate_json_parsing():
    """Simulate how the JSON might be getting parsed incorrectly."""
    
    print("=== SIMULACIÓN DE PARSING DE JSON ===")
    
    # JSON que podrías estar enviando (con números en lugar de strings)
    problematic_json = {
        "p_first_name": "MAXIMILIANO",
        "p_last_name": "SEIPIO REYES",
        "p_middle_name": "",
        "p_date_of_birth": None,
        "p_gender": "Masculino",
        "p_nationality_country": "República Dominicana",
        "p_marital_status": "Soltero",
        "p_occupation": "",
        "p_documents": [
            {
                "is_primary": True,
                "document_type": "Cédula",
                "document_number": "402-0019871-7",
                "issuing_country_id": 1,  # ❌ NÚMERO en lugar de string
                "document_issue_date": None,
                "document_expiry_date": None
            }
        ],
        "p_addresses": [
            {
                "address_line1": "ANGULO GURIDI CASA 13 VILLA PROVIDENCIA",
                "address_line2": "San Pedro de Macorís",
                "city_id": 1,  # ❌ NÚMERO en lugar de string
                "postal_code": "21008",
                "address_type": "Casa",
                "is_principal": True
            }
        ],
        "p_person_role_id": 1,
        "p_additional_data": {
            "phone_number": "829635244",
            "email": "g@gjvbv.cim",
            "photoPath": "/data/user/0/com.gcapital.gcapital_app/cache/extracted_face_1754335448418.jpg"
        }
    }
    
    print("JSON problemático (con números):")
    print(json.dumps(problematic_json, indent=2, ensure_ascii=False))
    print()
    
    try:
        PersonCompleteCreate(**problematic_json)
        print("❌ ERROR: Este JSON NO debería funcionar pero sí funciona")
    except Exception as e:
        print(f"✅ CORRECTO: Este JSON falla como esperado: {str(e)}")
    
    # JSON correcto (con strings)
    correct_json = {
        "p_first_name": "MAXIMILIANO",
        "p_last_name": "SEIPIO REYES",
        "p_middle_name": "",
        "p_date_of_birth": None,
        "p_gender": "Masculino",
        "p_nationality_country": "República Dominicana",
        "p_marital_status": "Soltero",
        "p_occupation": "",
        "p_documents": [
            {
                "is_primary": True,
                "document_type": "Cédula",
                "document_number": "402-0019871-7",
                "issuing_country_id": "1",  # ✅ STRING
                "document_issue_date": None,
                "document_expiry_date": None
            }
        ],
        "p_addresses": [
            {
                "address_line1": "ANGULO GURIDI CASA 13 VILLA PROVIDENCIA",
                "address_line2": "San Pedro de Macorís",
                "city_id": "1",  # ✅ STRING
                "postal_code": "21008",
                "address_type": "Casa",
                "is_principal": True
            }
        ],
        "p_person_role_id": 1,
        "p_additional_data": {
            "phone_number": "829635244",
            "email": "g@gjvbv.cim",
            "photoPath": "/data/user/0/com.gcapital.gcapital_app/cache/extracted_face_1754335448418.jpg"
        }
    }
    
    print("\nJSON correcto (con strings):")
    print(json.dumps(correct_json, indent=2, ensure_ascii=False))
    print()
    
    try:
        PersonCompleteCreate(**correct_json)
        print("✅ CORRECTO: Este JSON funciona como esperado")
    except Exception as e:
        print(f"❌ ERROR: Este JSON debería funcionar pero falla: {str(e)}")


def test_json_serialization():
    """Test how JSON might be getting serialized/deserialized."""
    
    print("\n=== PRUEBA DE SERIALIZACIÓN JSON ===")
    
    # Simular el JSON que podrías estar enviando
    original_json = {
        "p_first_name": "MAXIMILIANO",
        "p_last_name": "SEIPIO REYES",
        "p_middle_name": "",
        "p_date_of_birth": None,
        "p_gender": "Masculino",
        "p_nationality_country": "República Dominicana",
        "p_marital_status": "Soltero",
        "p_occupation": "",
        "p_documents": [
            {
                "is_primary": True,
                "document_type": "Cédula",
                "document_number": "402-0019871-7",
                "issuing_country_id": 1,  # Número
                "document_issue_date": None,
                "document_expiry_date": None
            }
        ],
        "p_addresses": [
            {
                "address_line1": "ANGULO GURIDI CASA 13 VILLA PROVIDENCIA",
                "address_line2": "San Pedro de Macorís",
                "city_id": 1,  # Número
                "postal_code": "21008",
                "address_type": "Casa",
                "is_principal": True
            }
        ],
        "p_person_role_id": 1,
        "p_additional_data": {
            "phone_number": "829635244",
            "email": "g@gjvbv.cim",
            "photoPath": "/data/user/0/com.gcapital.gcapital_app/cache/extracted_face_1754335448418.jpg"
        }
    }
    
    print("JSON original (con números):")
    print(json.dumps(original_json, indent=2, ensure_ascii=False))
    print()
    
    # Simular serialización/deserialización
    json_string = json.dumps(original_json)
    print("JSON serializado:")
    print(json_string)
    print()
    
    # Deserializar
    deserialized = json.loads(json_string)
    print("JSON deserializado:")
    print(json.dumps(deserialized, indent=2, ensure_ascii=False))
    print()
    
    # Verificar tipos
    print("Tipos de datos:")
    print(f"  issuing_country_id: {type(deserialized['p_documents'][0]['issuing_country_id'])} = {deserialized['p_documents'][0]['issuing_country_id']}")
    print(f"  city_id: {type(deserialized['p_addresses'][0]['city_id'])} = {deserialized['p_addresses'][0]['city_id']}")
    
    try:
        PersonCompleteCreate(**deserialized)
        print("❌ ERROR: El JSON deserializado NO debería funcionar")
    except Exception as e:
        print(f"✅ CORRECTO: El JSON deserializado falla como esperado: {str(e)}")


def create_fixed_json():
    """Create the definitively fixed JSON."""
    
    print("\n=== JSON DEFINITIVAMENTE CORREGIDO ===")
    
    fixed_json = {
        "p_first_name": "MAXIMILIANO",
        "p_last_name": "SEIPIO REYES",
        "p_middle_name": "",
        "p_date_of_birth": None,
        "p_gender": "Masculino",
        "p_nationality_country": "República Dominicana",
        "p_marital_status": "Soltero",
        "p_occupation": "",
        "p_documents": [
            {
                "is_primary": True,
                "document_type": "Cédula",
                "document_number": "402-0019871-7",
                "issuing_country_id": "1",
                "document_issue_date": None,
                "document_expiry_date": None
            }
        ],
        "p_addresses": [
            {
                "address_line1": "ANGULO GURIDI CASA 13 VILLA PROVIDENCIA",
                "address_line2": "San Pedro de Macorís",
                "city_id": "1",
                "postal_code": "21008",
                "address_type": "Casa",
                "is_principal": True
            }
        ],
        "p_person_role_id": 1,
        "p_additional_data": {
            "phone_number": "829635244",
            "email": "g@gjvbv.cim",
            "photoPath": "/data/user/0/com.gcapital.gcapital_app/cache/extracted_face_1754335448418.jpg"
        }
    }
    
    print("JSON definitivamente corregido:")
    print(json.dumps(fixed_json, indent=2, ensure_ascii=False))
    print()
    
    try:
        PersonCompleteCreate(**fixed_json)
        print("✅ CORRECTO: Este JSON funciona perfectamente")
        
        # Guardar en archivo
        with open("json_definitivo.json", "w", encoding="utf-8") as f:
            json.dump(fixed_json, f, indent=2, ensure_ascii=False)
        print("✅ JSON guardado en 'json_definitivo.json'")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def main():
    """Main debug function."""
    print("🚀 Iniciando Debug del Problema JSON")
    print("=" * 60)
    
    # Test 1: Simulación de parsing
    simulate_json_parsing()
    
    # Test 2: Serialización JSON
    test_json_serialization()
    
    # Test 3: JSON definitivo
    create_fixed_json()
    
    print("\n" + "=" * 60)
    print("🏁 Resumen del Debug")
    print("=" * 60)
    print("El problema es que estás enviando números en lugar de strings")
    print("para 'issuing_country_id' y 'city_id'.")
    print("\nSOLUCIÓN: Usa el archivo 'json_definitivo.json' que se creó.")


if __name__ == "__main__":
    main() 