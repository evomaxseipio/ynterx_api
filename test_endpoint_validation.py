#!/usr/bin/env python3
"""
Test script to validate JSON against the actual endpoint validation.
"""

import json
from typing import Dict, Any

from app.person.schemas import PersonCompleteCreate, PersonDocumentCreate, PersonAddressCreate


# JSON exacto que estás enviando
TEST_JSON = {
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


def test_direct_validation():
    """Test direct validation with the schema."""
    
    print("=== VALIDACIÓN DIRECTA CON SCHEMA ===")
    print(f"JSON a validar: {json.dumps(TEST_JSON, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        # Intentar crear el schema directamente
        person_data = PersonCompleteCreate(**TEST_JSON)
        print("✅ Validación exitosa!")
        print(f"Schema creado: {type(person_data)}")
        return True
    except Exception as e:
        print(f"❌ Error de validación: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        return False


def test_field_by_field():
    """Test each field individually to identify the problem."""
    
    print("\n=== VALIDACIÓN CAMPO POR CAMPO ===")
    
    # Campos básicos
    basic_fields = [
        "p_first_name", "p_last_name", "p_middle_name", "p_date_of_birth",
        "p_gender", "p_nationality_country", "p_marital_status", "p_occupation",
        "p_person_role_id"
    ]
    
    print("Verificando campos básicos...")
    for field in basic_fields:
        if field in TEST_JSON:
            value = TEST_JSON[field]
            print(f"  ✅ {field}: {value} ({type(value).__name__})")
        else:
            print(f"  ❌ {field}: Faltante")
    
    # Documentos
    print("\nVerificando documentos...")
    if "p_documents" in TEST_JSON and TEST_JSON["p_documents"]:
        for i, doc in enumerate(TEST_JSON["p_documents"]):
            print(f"  Documento {i+1}:")
            doc_fields = ["is_primary", "document_type", "document_number", "issuing_country_id"]
            for field in doc_fields:
                if field in doc:
                    value = doc[field]
                    print(f"    ✅ {field}: {value} ({type(value).__name__})")
                else:
                    print(f"    ❌ {field}: Faltante")
    
    # Direcciones
    print("\nVerificando direcciones...")
    if "p_addresses" in TEST_JSON and TEST_JSON["p_addresses"]:
        for i, addr in enumerate(TEST_JSON["p_addresses"]):
            print(f"  Dirección {i+1}:")
            addr_fields = ["address_line1", "address_line2", "city_id", "postal_code", "address_type", "is_principal"]
            for field in addr_fields:
                if field in addr:
                    value = addr[field]
                    print(f"    ✅ {field}: {value} ({type(value).__name__})")
                else:
                    print(f"    ❌ {field}: Faltante")
    
    # Datos adicionales
    print("\nVerificando datos adicionales...")
    if "p_additional_data" in TEST_JSON and TEST_JSON["p_additional_data"]:
        for key, value in TEST_JSON["p_additional_data"].items():
            print(f"  ✅ {key}: {value} ({type(value).__name__})")


def test_schema_requirements():
    """Test against the actual schema requirements."""
    
    print("\n=== REQUISITOS DEL SCHEMA ===")
    
    # Verificar PersonDocumentCreate
    print("Requisitos PersonDocumentCreate:")
    doc_schema = PersonDocumentCreate.model_json_schema()
    print(f"  - issuing_country_id: {doc_schema['properties']['issuing_country_id']}")
    
    # Verificar PersonAddressCreate
    print("\nRequisitos PersonAddressCreate:")
    addr_schema = PersonAddressCreate.model_json_schema()
    print(f"  - city_id: {addr_schema['properties']['city_id']}")
    
    # Verificar PersonCompleteCreate
    print("\nRequisitos PersonCompleteCreate:")
    complete_schema = PersonCompleteCreate.model_json_schema()
    print(f"  - p_documents: {complete_schema['properties']['p_documents']}")
    print(f"  - p_addresses: {complete_schema['properties']['p_addresses']}")


def test_alternative_formats():
    """Test different formats to see what works."""
    
    print("\n=== PRUEBAS CON FORMATOS ALTERNATIVOS ===")
    
    # Probar con diferentes formatos de IDs
    test_cases = [
        {
            "name": "IDs como strings",
            "data": {
                **TEST_JSON,
                "p_documents": [{**TEST_JSON["p_documents"][0], "issuing_country_id": "1"}],
                "p_addresses": [{**TEST_JSON["p_addresses"][0], "city_id": "1"}]
            }
        },
        {
            "name": "IDs como integers",
            "data": {
                **TEST_JSON,
                "p_documents": [{**TEST_JSON["p_documents"][0], "issuing_country_id": 1}],
                "p_addresses": [{**TEST_JSON["p_addresses"][0], "city_id": 1}]
            }
        },
        {
            "name": "Sin documentos",
            "data": {**TEST_JSON, "p_documents": None}
        },
        {
            "name": "Sin direcciones",
            "data": {**TEST_JSON, "p_addresses": None}
        },
        {
            "name": "Sin datos adicionales",
            "data": {**TEST_JSON, "p_additional_data": None}
        }
    ]
    
    for test_case in test_cases:
        try:
            PersonCompleteCreate(**test_case["data"])
            print(f"✅ {test_case['name']}: Funciona")
        except Exception as e:
            print(f"❌ {test_case['name']}: {str(e)}")


def main():
    """Main test function."""
    print("🚀 Iniciando Pruebas de Validación de Endpoint")
    print("=" * 60)
    
    # Test 1: Validación directa
    direct_ok = test_direct_validation()
    
    # Test 2: Campo por campo
    test_field_by_field()
    
    # Test 3: Requisitos del schema
    test_schema_requirements()
    
    # Test 4: Formatos alternativos
    test_alternative_formats()
    
    print("\n" + "=" * 60)
    print("🏁 Resumen de Pruebas")
    print("=" * 60)
    
    if direct_ok:
        print("✅ El JSON debería funcionar correctamente")
        print("   Si aún tienes error 422, puede ser un problema de:")
        print("   - Autenticación (token inválido)")
        print("   - Headers de la petición")
        print("   - Formato de envío (Content-Type)")
    else:
        print("❌ El JSON tiene problemas de validación")
        print("   Revisa los errores específicos arriba")


if __name__ == "__main__":
    main() 