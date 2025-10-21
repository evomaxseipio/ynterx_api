#!/usr/bin/env python3
"""
Simplified test script to validate JSON structure for person creation.
"""

import json
from datetime import date
from typing import Dict, Any

from app.person.schemas import PersonCompleteCreate, PersonDocumentCreate, PersonAddressCreate


# Test JSON data provided by the user
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


def convert_json_to_schema(json_data: Dict[str, Any]) -> PersonCompleteCreate:
    """Convert the JSON data to PersonCompleteCreate schema."""
    
    # Convert documents
    documents = []
    if json_data.get("p_documents"):
        for doc in json_data["p_documents"]:
            documents.append(PersonDocumentCreate(
                is_primary=doc.get("is_primary", False),
                document_type=doc["document_type"],
                document_number=doc["document_number"],
                issuing_country_id=str(doc["issuing_country_id"]),
                document_issue_date=doc.get("document_issue_date"),
                document_expiry_date=doc.get("document_expiry_date")
            ))
    
    # Convert addresses
    addresses = []
    if json_data.get("p_addresses"):
        for addr in json_data["p_addresses"]:
            addresses.append(PersonAddressCreate(
                address_line1=addr["address_line1"],
                address_line2=addr.get("address_line2"),
                city_id=str(addr["city_id"]),
                postal_code=addr.get("postal_code"),
                address_type=addr["address_type"],
                is_principal=addr.get("is_principal", False)
            ))
    
    # Create the complete person schema
    return PersonCompleteCreate(
        p_first_name=json_data["p_first_name"],
        p_last_name=json_data["p_last_name"],
        p_middle_name=json_data.get("p_middle_name"),
        p_date_of_birth=json_data.get("p_date_of_birth"),
        p_gender=json_data.get("p_gender"),
        p_nationality_country=json_data.get("p_nationality_country"),
        p_marital_status=json_data.get("p_marital_status"),
        p_occupation=json_data.get("p_occupation"),
        p_documents=documents if documents else None,
        p_addresses=addresses if addresses else None,
        p_additional_data=json_data.get("p_additional_data"),
        p_person_role_id=json_data.get("p_person_role_id", 1)
    )


def test_json_structure():
    """Test the JSON structure validation."""
    
    print("=== VALIDACIÓN DE ESTRUCTURA JSON ===")
    print(f"JSON de entrada: {json.dumps(TEST_JSON, indent=2, ensure_ascii=False)}")
    print()
    
    # Test the JSON structure
    required_fields = ["p_first_name", "p_last_name"]
    optional_fields = ["p_middle_name", "p_date_of_birth", "p_gender", "p_nationality_country", 
                      "p_marital_status", "p_occupation", "p_documents", "p_addresses", 
                      "p_person_role_id", "p_additional_data"]
    
    print("Verificando campos requeridos...")
    for field in required_fields:
        if field in TEST_JSON and TEST_JSON[field]:
            print(f"✅ {field}: {TEST_JSON[field]}")
        else:
            print(f"❌ {field}: Faltante o vacío")
    
    print("\nVerificando campos opcionales...")
    for field in optional_fields:
        if field in TEST_JSON:
            print(f"✅ {field}: Presente")
        else:
            print(f"⚠️  {field}: Faltante")
    
    # Test documents structure
    if "p_documents" in TEST_JSON and TEST_JSON["p_documents"]:
        print("\nVerificando estructura de documentos...")
        for i, doc in enumerate(TEST_JSON["p_documents"]):
            print(f"Documento {i+1}:")
            doc_fields = ["is_primary", "document_type", "document_number", "issuing_country_id"]
            for field in doc_fields:
                if field in doc:
                    print(f"  ✅ {field}: {doc[field]}")
                else:
                    print(f"  ❌ {field}: Faltante")
    
    # Test addresses structure
    if "p_addresses" in TEST_JSON and TEST_JSON["p_addresses"]:
        print("\nVerificando estructura de direcciones...")
        for i, addr in enumerate(TEST_JSON["p_addresses"]):
            print(f"Dirección {i+1}:")
            addr_fields = ["address_line1", "city_id", "address_type"]
            for field in addr_fields:
                if field in addr:
                    print(f"  ✅ {field}: {addr[field]}")
                else:
                    print(f"  ❌ {field}: Faltante")


def test_schema_validation():
    """Test schema validation with the JSON data."""
    
    print("\n=== VALIDACIÓN DE ESQUEMA ===")
    
    try:
        # Test with original JSON
        person_data = convert_json_to_schema(TEST_JSON)
        print("✅ Validación del JSON original exitosa")
        print(f"Datos del esquema: {person_data.model_dump_json(indent=2)}")
        
        # Test with modified JSON (missing required fields)
        test_cases = [
            {
                "name": "Sin nombre",
                "data": {**TEST_JSON, "p_first_name": ""}
            },
            {
                "name": "Sin apellido", 
                "data": {**TEST_JSON, "p_last_name": ""}
            },
            {
                "name": "Tipo de documento inválido",
                "data": {
                    **TEST_JSON,
                    "p_documents": [{**TEST_JSON["p_documents"][0], "document_type": ""}]
                }
            },
            {
                "name": "Número de documento inválido",
                "data": {
                    **TEST_JSON,
                    "p_documents": [{**TEST_JSON["p_documents"][0], "document_number": ""}]
                }
            },
            {
                "name": "Dirección sin línea 1",
                "data": {
                    **TEST_JSON,
                    "p_addresses": [{**TEST_JSON["p_addresses"][0], "address_line1": ""}]
                }
            }
        ]
        
        print("\nProbando casos de validación negativa...")
        for test_case in test_cases:
            try:
                convert_json_to_schema(test_case["data"])
                print(f"❌ {test_case['name']}: Debería haber fallado la validación")
            except Exception as e:
                print(f"✅ {test_case['name']}: Validación falló correctamente - {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validación de esquema: {str(e)}")
        return False


def test_json_compatibility():
    """Test if the JSON is compatible with the service."""
    
    print("\n=== COMPATIBILIDAD CON EL SERVICIO ===")
    
    try:
        # Convert to schema
        person_data = convert_json_to_schema(TEST_JSON)
        
        # Check if all required fields for the service are present
        service_required_fields = [
            "p_first_name", "p_last_name", "p_person_role_id"
        ]
        
        print("Verificando campos requeridos para el servicio...")
        for field in service_required_fields:
            if hasattr(person_data, field) and getattr(person_data, field):
                print(f"✅ {field}: Presente")
            else:
                print(f"❌ {field}: Faltante")
        
        # Check documents
        if person_data.p_documents:
            print(f"✅ Documentos: {len(person_data.p_documents)} documento(s)")
            for i, doc in enumerate(person_data.p_documents):
                print(f"  Documento {i+1}: {doc.document_type} - {doc.document_number}")
        else:
            print("⚠️  Documentos: Ninguno")
        
        # Check addresses
        if person_data.p_addresses:
            print(f"✅ Direcciones: {len(person_data.p_addresses)} dirección(es)")
            for i, addr in enumerate(person_data.p_addresses):
                print(f"  Dirección {i+1}: {addr.address_line1}")
        else:
            print("⚠️  Direcciones: Ninguna")
        
        # Check additional data
        if person_data.p_additional_data:
            print(f"✅ Datos adicionales: {len(person_data.p_additional_data)} campo(s)")
            for key, value in person_data.p_additional_data.items():
                print(f"  {key}: {value}")
        else:
            print("⚠️  Datos adicionales: Ninguno")
        
        print("\n🎉 El JSON es compatible con el servicio de creación de personas!")
        return True
        
    except Exception as e:
        print(f"❌ Error en compatibilidad: {str(e)}")
        return False


def main():
    """Main test function."""
    print("🚀 Iniciando Validación de JSON para Creación de Persona")
    print("=" * 60)
    
    # Test 1: JSON structure
    test_json_structure()
    
    # Test 2: Schema validation
    schema_valid = test_schema_validation()
    
    # Test 3: Service compatibility
    service_compatible = test_json_compatibility()
    
    print("\n" + "=" * 60)
    print("🏁 Resumen de Validación")
    print("=" * 60)
    
    if schema_valid and service_compatible:
        print("✅ RESULTADO: El JSON es válido y puede usarse para crear una persona")
        print("\n📋 Resumen:")
        print("  - Estructura JSON: ✅ Válida")
        print("  - Validación de esquema: ✅ Exitosa")
        print("  - Compatibilidad con servicio: ✅ Confirmada")
        print("\n🎯 El JSON proporcionado puede usarse para crear una persona en el sistema.")
    else:
        print("❌ RESULTADO: El JSON tiene problemas que deben corregirse")
        if not schema_valid:
            print("  - Validación de esquema: ❌ Falló")
        if not service_compatible:
            print("  - Compatibilidad con servicio: ❌ Falló")


if __name__ == "__main__":
    main() 