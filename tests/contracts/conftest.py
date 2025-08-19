"""
Fixtures comunes para pruebas de contratos
"""
import pytest
import asyncio
from typing import Dict, Any
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Cliente de prueba para FastAPI"""
    return TestClient(app)

@pytest.fixture
def base_contract_data() -> Dict[str, Any]:
    """Datos base para contratos de prueba"""
    return {
        "contract_type": "mortgage",
        "contract_type_id": 1,
        "description": "Contrato de prueba",
        "contract_date": "15/08/2025",
        "contract_end_date": "15/08/2026",
        "paragraph_request": [
            {
                "person_role": "client",
                "contract_type": "fisica_soltera",
                "section": "identification",
                "contract_services": "mortgage"
            },
            {
                "person_role": "investor",
                "contract_type": "fisica_soltera",
                "section": "identification",
                "contract_services": "mortgage"
            }
        ],
        "loan": {
            "amount": 20000.0,
            "currency": "USD",
            "interest_rate": 2.2,
            "term_months": 12,
            "loan_type": "Hipotecario",
            "loan_payments_details": {
                "monthly_payment": 440.0,
                "final_payment": 20440.0,
                "discount_rate": 0.2,
                "payment_qty_quotes": 11,
                "payment_type": "Mensual"
            },
            "bank_account": {
                "bank_name": "Banco Test",
                "bank_account_number": "1234567890",
                "bank_account_type": "Corriente",
                "bank_account_currency": "USD"
            }
        },
        "properties": [
            {
                "property_type": "casa",
                "cadastral_number": "TEST-001",
                "title_number": "4000000001",
                "surface_area": 100.0,
                "covered_area": 80.0,
                "property_value": 20000.0,
                "currency": "USD",
                "description": "Propiedad de prueba",
                "address_line1": "Calle Test 123",
                "address_line2": "Sector Test",
                "city_id": "1",
                "postal_code": "21000",
                "property_role": "garantia"
            }
        ],
        "clients": [],
        "investors": [],
        "witnesses": [],
        "referents": [],
        "notary": []
    }

@pytest.fixture
def person_fisica_soltera() -> Dict[str, Any]:
    """Datos de persona física soltera"""
    return {
        "person": {
            "p_first_name": "Juan",
            "p_last_name": "Pérez",
            "p_middle_name": "",
            "p_date_of_birth": "1990-01-01",
            "p_gender": "Masculino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Soltero",
            "p_occupation": "Ingeniero",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "123-4567890-1",
                    "issuing_country_id": "1",
                    "document_issue_date": "2010-01-01",
                    "document_expiry_date": "2030-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Calle Principal 123",
                    "address_line2": "Sector Centro",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Casa",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 1,
            "p_additional_data": {
                "phone_number": "8091234567",
                "email": "juan.perez@test.com"
            }
        }
    }

@pytest.fixture
def person_fisica_casada() -> Dict[str, Any]:
    """Datos de persona física casada"""
    return {
        "person": {
            "p_first_name": "María",
            "p_last_name": "García",
            "p_middle_name": "",
            "p_date_of_birth": "1985-05-15",
            "p_gender": "Femenino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Casada",
            "p_occupation": "Abogada",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "987-6543210-9",
                    "issuing_country_id": "1",
                    "document_issue_date": "2015-01-01",
                    "document_expiry_date": "2035-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Avenida Principal 456",
                    "address_line2": "Sector Norte",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Casa",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 1,
            "p_additional_data": {
                "phone_number": "8099876543",
                "email": "maria.garcia@test.com"
            }
        }
    }

@pytest.fixture
def person_juridica_soltera() -> Dict[str, Any]:
    """Datos de persona jurídica soltera"""
    return {
        "person": {
            "p_first_name": "Carlos",
            "p_last_name": "Rodríguez",
            "p_middle_name": "",
            "p_date_of_birth": "1988-12-20",
            "p_gender": "Masculino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Soltero",
            "p_occupation": "Empresario",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "555-1111111-5",
                    "issuing_country_id": "1",
                    "document_issue_date": "2012-01-01",
                    "document_expiry_date": "2032-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Calle Comercial 789",
                    "address_line2": "Sector Empresarial",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Oficina",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 1,
            "p_additional_data": {
                "phone_number": "8095551111",
                "email": "carlos.rodriguez@test.com"
            },
            "is_juridical": True  # Campo para identificar persona jurídica
        }
    }

@pytest.fixture
def person_juridica_casada() -> Dict[str, Any]:
    """Datos de persona jurídica casada"""
    return {
        "person": {
            "p_first_name": "Ana",
            "p_last_name": "López",
            "p_middle_name": "",
            "p_date_of_birth": "1982-08-10",
            "p_gender": "Femenino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Casada",
            "p_occupation": "Directora",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "777-9999999-7",
                    "issuing_country_id": "1",
                    "document_issue_date": "2018-01-01",
                    "document_expiry_date": "2038-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Avenida Ejecutiva 321",
                    "address_line2": "Sector Corporativo",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Oficina",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 1,
            "p_additional_data": {
                "phone_number": "8097779999",
                "email": "ana.lopez@test.com"
            },
            "is_juridical": True  # Campo para identificar persona jurídica
        }
    }

@pytest.fixture
def company_data() -> Dict[str, Any]:
    """Datos de empresa"""
    return {
        "company_name": "Empresa Test S.R.L.",
        "company_rnc": "123-4567890-1",
        "company_mercantil_number": "TEST123",
        "company_phone": "(809) 123-4567",
        "company_email": "info@empresatest.com",
        "company_type": "Servicios",
        "company_address": {
            "address_line1": "Calle Empresarial 100",
            "city": "Santo Domingo",
            "postal_code": "10100",
            "phone_number": "(809) 123-4567",
            "email": "info@empresatest.com"
        },
        "company_manager": [
            {
                "name": "Gerente Test",
                "position": "Gerente General",
                "document_number": "111-2223333-4",
                "nationality": "Dominicana",
                "marital_status": "Casado",
                "address": "Calle Gerente 200",
                "is_main_manager": True
            }
        ]
    }

@pytest.fixture
def witness_data() -> Dict[str, Any]:
    """Datos de testigo"""
    return {
        "person": {
            "p_first_name": "Testigo",
            "p_last_name": "Apellido",
            "p_middle_name": "",
            "p_date_of_birth": "1975-03-15",
            "p_gender": "Masculino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Casado",
            "p_occupation": "Testigo",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "333-4445555-6",
                    "issuing_country_id": "1",
                    "document_issue_date": "2000-01-01",
                    "document_expiry_date": "2020-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Calle Testigo 300",
                    "address_line2": "Sector Testigo",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Casa",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 3,
            "p_additional_data": {
                "phone_number": "8093334444",
                "email": "testigo@test.com"
            }
        }
    }

@pytest.fixture
def referent_data() -> Dict[str, Any]:
    """Datos de referidor"""
    return {
        "person": {
            "p_first_name": "Referidor",
            "p_last_name": "Apellido",
            "p_middle_name": "",
            "p_date_of_birth": "1980-07-22",
            "p_gender": "Femenino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Soltera",
            "p_occupation": "Referidor",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "666-7778888-9",
                    "issuing_country_id": "1",
                    "document_issue_date": "2005-01-01",
                    "document_expiry_date": "2025-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Calle Referidor 400",
                    "address_line2": "Sector Referidor",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Casa",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 8,
            "p_additional_data": {
                "phone_number": "8096667777",
                "email": "referidor@test.com"
            }
        }
    }

@pytest.fixture
def notary_data() -> Dict[str, Any]:
    """Datos de notario"""
    return {
        "person": {
            "p_first_name": "Notario",
            "p_last_name": "Apellido",
            "p_middle_name": "",
            "p_date_of_birth": "1970-11-30",
            "p_gender": "Masculino",
            "p_nationality_country": "Republica Dominicana",
            "p_marital_status": "Casado",
            "p_occupation": "Notario",
            "p_documents": [
                {
                    "is_primary": True,
                    "document_type": "Cédula",
                    "document_number": "999-0001111-2",
                    "issuing_country_id": "1",
                    "document_issue_date": "1995-01-01",
                    "document_expiry_date": "2015-01-01"
                }
            ],
            "p_addresses": [
                {
                    "address_line1": "Calle Notario 500",
                    "address_line2": "Sector Notario",
                    "city_id": "1",
                    "postal_code": "21000",
                    "address_type": "Oficina",
                    "is_principal": True
                }
            ],
            "p_person_role_id": 7,
            "p_additional_data": {
                "notary_id": "test-notary-id",
                "license_number": "1234"
            }
        }
    }
