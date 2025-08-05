#!/usr/bin/env python3
"""
Test script for the person service with the provided JSON data.
"""

import asyncio
import json
from datetime import date
from uuid import uuid4
from typing import Dict, Any

from app.database import get_db_connection, engine
from app.person.service import PersonService
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


async def test_person_creation():
    """Test the person creation with the provided JSON."""
    
    print("=== TESTING PERSON CREATION ===")
    print(f"Input JSON: {json.dumps(TEST_JSON, indent=2, ensure_ascii=False)}")
    print()
    
    try:
        # Convert JSON to schema
        person_data = convert_json_to_schema(TEST_JSON)
        print("✅ JSON converted to schema successfully")
        print(f"Schema data: {person_data.model_dump_json(indent=2)}")
        print()
        
        # Get database connection
        connection = await engine.connect()
        try:
            print("✅ Database connection established")
            
            # Test person creation
            print("🔄 Creating person...")
            result = await PersonService.create_person_complete(
                person_data=person_data,
                connection=connection,
                created_by=uuid4(),
                updated_by=uuid4()
            )
            
            print("✅ Person creation completed")
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
            
            if result.get("success"):
                print("🎉 Person created successfully!")
                if result.get("person_id"):
                    print(f"Person ID: {result['person_id']}")
                
                # Test retrieving the created person
                if result.get("person_id"):
                    print("\n🔄 Retrieving created person...")
                    person = await PersonService.get_person(
                        person_id=result["person_id"],
                        connection=connection
                    )
                    if person:
                        print("✅ Person retrieved successfully")
                        print(f"Retrieved person: {json.dumps(dict(person), indent=2, ensure_ascii=False, default=str)}")
                    else:
                        print("❌ Failed to retrieve person")
            else:
                print("❌ Person creation failed!")
                if result.get("errors"):
                    print("Errors:")
                    for error in result["errors"]:
                        print(f"  - {error}")
        finally:
            await connection.close()
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_schema_validation():
    """Test schema validation with the JSON data."""
    
    print("\n=== TESTING SCHEMA VALIDATION ===")
    
    try:
        # Test with original JSON
        person_data = convert_json_to_schema(TEST_JSON)
        print("✅ Original JSON validation passed")
        
        # Test with modified JSON (missing required fields)
        test_cases = [
            {
                "name": "Missing first_name",
                "data": {**TEST_JSON, "p_first_name": ""}
            },
            {
                "name": "Missing last_name", 
                "data": {**TEST_JSON, "p_last_name": ""}
            },
            {
                "name": "Invalid document type",
                "data": {
                    **TEST_JSON,
                    "p_documents": [{**TEST_JSON["p_documents"][0], "document_type": ""}]
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                convert_json_to_schema(test_case["data"])
                print(f"❌ {test_case['name']}: Should have failed validation")
            except Exception as e:
                print(f"✅ {test_case['name']}: Validation correctly failed - {str(e)}")
        
    except Exception as e:
        print(f"❌ Schema validation error: {str(e)}")


async def test_json_parsing():
    """Test JSON parsing and structure validation."""
    
    print("\n=== TESTING JSON PARSING ===")
    
    # Test the JSON structure
    required_fields = ["p_first_name", "p_last_name"]
    optional_fields = ["p_middle_name", "p_date_of_birth", "p_gender", "p_nationality_country", 
                      "p_marital_status", "p_occupation", "p_documents", "p_addresses", 
                      "p_person_role_id", "p_additional_data"]
    
    print("Checking required fields...")
    for field in required_fields:
        if field in TEST_JSON and TEST_JSON[field]:
            print(f"✅ {field}: {TEST_JSON[field]}")
        else:
            print(f"❌ {field}: Missing or empty")
    
    print("\nChecking optional fields...")
    for field in optional_fields:
        if field in TEST_JSON:
            print(f"✅ {field}: Present")
        else:
            print(f"⚠️  {field}: Missing")
    
    # Test documents structure
    if "p_documents" in TEST_JSON and TEST_JSON["p_documents"]:
        print("\nChecking documents structure...")
        for i, doc in enumerate(TEST_JSON["p_documents"]):
            print(f"Document {i+1}:")
            doc_fields = ["is_primary", "document_type", "document_number", "issuing_country_id"]
            for field in doc_fields:
                if field in doc:
                    print(f"  ✅ {field}: {doc[field]}")
                else:
                    print(f"  ❌ {field}: Missing")
    
    # Test addresses structure
    if "p_addresses" in TEST_JSON and TEST_JSON["p_addresses"]:
        print("\nChecking addresses structure...")
        for i, addr in enumerate(TEST_JSON["p_addresses"]):
            print(f"Address {i+1}:")
            addr_fields = ["address_line1", "city_id", "address_type"]
            for field in addr_fields:
                if field in addr:
                    print(f"  ✅ {field}: {addr[field]}")
                else:
                    print(f"  ❌ {field}: Missing")


async def main():
    """Main test function."""
    print("🚀 Starting Person Service Tests")
    print("=" * 50)
    
    # Test 1: JSON parsing
    await test_json_parsing()
    
    # Test 2: Schema validation
    await test_schema_validation()
    
    # Test 3: Person creation
    await test_person_creation()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed")


if __name__ == "__main__":
    asyncio.run(main()) 