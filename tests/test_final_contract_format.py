import json
from typing import Dict, Any, List


def load_final_contract() -> Dict[str, Any]:
    """Load the final contract JSON file"""
    with open('app/json/final_contract.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def test_contract_structure():
    """Test the overall structure of the final contract"""
    contract = load_final_contract()
    
    # Test main contract fields
    assert 'contract_type' in contract
    assert 'contract_type_id' in contract
    assert 'contract_date' in contract
    assert 'contract_end_date' in contract
    assert 'client_company' in contract
    assert 'investor_company' in contract
    assert 'paragraph_request' in contract
    assert 'loan' in contract
    assert 'properties' in contract
    assert 'clients' in contract
    assert 'investors' in contract
    assert 'witnesses' in contract
    assert 'referents' in contract
    assert 'notary' in contract


def test_person_fields_have_p_prefix():
    """Test that all person fields have the p_ prefix"""
    contract = load_final_contract()
    
    # Check clients
    for client in contract['clients']:
        person = client['person']
        assert 'p_first_name' in person
        assert 'p_last_name' in person
        assert 'p_middle_name' in person
        assert 'p_date_of_birth' in person
        assert 'p_gender' in person
        assert 'p_nationality_country' in person
        assert 'p_marital_status' in person
        assert 'p_occupation' in person
        assert 'p_documents' in person
        assert 'p_addresses' in person
        assert 'p_person_role_id' in person
        assert 'p_additional_data' in person
    
    # Check investors
    for investor in contract['investors']:
        person = investor['person']
        assert 'p_first_name' in person
        assert 'p_last_name' in person
        assert 'p_middle_name' in person
        assert 'p_date_of_birth' in person
        assert 'p_gender' in person
        assert 'p_nationality_country' in person
        assert 'p_marital_status' in person
        assert 'p_occupation' in person
        assert 'p_documents' in person
        assert 'p_addresses' in person
        assert 'p_person_role_id' in person
        assert 'p_additional_data' in person
    
    # Check witnesses
    for witness in contract['witnesses']:
        person = witness['person']
        assert 'p_first_name' in person
        assert 'p_last_name' in person
        assert 'p_middle_name' in person
        assert 'p_date_of_birth' in person
        assert 'p_gender' in person
        assert 'p_nationality_country' in person
        assert 'p_marital_status' in person
        assert 'p_occupation' in person
        assert 'p_documents' in person
        assert 'p_addresses' in person
        assert 'p_person_role_id' in person
        assert 'p_additional_data' in person
    
    # Check notary
    for notary in contract['notary']:
        person = notary['person']
        assert 'p_first_name' in person
        assert 'p_last_name' in person
        assert 'p_middle_name' in person
        assert 'p_date_of_birth' in person
        assert 'p_gender' in person
        assert 'p_nationality_country' in person
        assert 'p_marital_status' in person
        assert 'p_occupation' in person
        assert 'p_documents' in person
        assert 'p_addresses' in person
        assert 'p_person_role_id' in person
        assert 'p_additional_data' in person


def test_person_role_ids():
    """Test that person role IDs are correctly assigned"""
    contract = load_final_contract()
    
    # Check role IDs
    for client in contract['clients']:
        assert client['person']['p_person_role_id'] == 1  # client
    
    for investor in contract['investors']:
        assert investor['person']['p_person_role_id'] == 2  # investor
    
    for witness in contract['witnesses']:
        assert witness['person']['p_person_role_id'] == 3  # witness
    
    for notary in contract['notary']:
        assert notary['person']['p_person_role_id'] == 7  # notary


def test_document_structure():
    """Test that documents have the correct structure"""
    contract = load_final_contract()
    
    for person_type in ['clients', 'investors', 'witnesses', 'notary']:
        for person_data in contract[person_type]:
            documents = person_data['person']['p_documents']
            for doc in documents:
                assert 'is_primary' in doc
                assert 'document_type' in doc
                assert 'document_number' in doc
                assert 'issuing_country_id' in doc
                assert 'document_issue_date' in doc
                assert 'document_expiry_date' in doc


def test_address_structure():
    """Test that addresses have the correct structure"""
    contract = load_final_contract()
    
    for person_type in ['clients', 'investors', 'witnesses', 'notary']:
        for person_data in contract[person_type]:
            addresses = person_data['person']['p_addresses']
            for addr in addresses:
                assert 'address_line1' in addr
                assert 'address_line2' in addr
                assert 'city_id' in addr
                assert 'postal_code' in addr
                assert 'address_type' in addr
                assert 'is_principal' in addr


def test_loan_structure():
    """Test that loan data has the correct structure"""
    contract = load_final_contract()
    loan = contract['loan']
    
    assert 'amount' in loan
    assert 'currency' in loan
    assert 'interest_rate' in loan
    assert 'term_months' in loan
    assert 'loan_type' in loan
    assert 'loan_payments_details' in loan
    assert 'bank_account' in loan
    
    # Check loan payments details
    payments = loan['loan_payments_details']
    assert 'monthly_payment' in payments
    assert 'final_payment' in payments
    assert 'discount_rate' in payments
    assert 'payment_qty_quotes' in payments
    assert 'payment_type' in payments
    
    # Check bank account
    bank = loan['bank_account']
    assert 'bank_name' in bank
    assert 'bank_account_number' in bank
    assert 'bank_account_type' in bank
    assert 'bank_account_currency' in bank


def test_property_structure():
    """Test that property data has the correct structure"""
    contract = load_final_contract()
    
    for property_data in contract['properties']:
        assert 'property_type' in property_data
        assert 'cadastral_number' in property_data
        assert 'title_number' in property_data
        assert 'surface_area' in property_data
        assert 'covered_area' in property_data
        assert 'property_value' in property_data
        assert 'currency' in property_data
        assert 'description' in property_data
        assert 'address_line1' in property_data
        assert 'address_line2' in property_data
        assert 'city_id' in property_data
        assert 'postal_code' in property_data
        assert 'property_role' in property_data
        assert 'owner_name' in property_data
        assert 'owner_document_number' in property_data
        assert 'owner_nationality' in property_data
        assert 'owner_civil_status' in property_data


def test_company_structure():
    """Test that company data has the correct structure"""
    contract = load_final_contract()
    
    # Check client company
    client_company = contract['client_company']
    assert 'name' in client_company
    assert 'rnc' in client_company
    assert 'rm' in client_company
    assert 'role' in client_company
    assert client_company['role'] == 'client'
    
    # Check investor company
    investor_company = contract['investor_company']
    assert 'name' in investor_company
    assert 'rnc' in investor_company
    assert 'rm' in investor_company
    assert 'role' in investor_company
    assert investor_company['role'] == 'investor'


def test_paragraph_request_structure():
    """Test that paragraph request has the correct structure"""
    contract = load_final_contract()
    
    for request in contract['paragraph_request']:
        assert 'person_role' in request
        assert 'contract_type' in request
        assert 'section' in request
        assert 'contract_services' in request


def test_data_types():
    """Test that data types are correct"""
    contract = load_final_contract()
    
    # Test numeric fields
    assert isinstance(contract['loan']['amount'], (int, float))
    assert isinstance(contract['loan']['interest_rate'], (int, float))
    assert isinstance(contract['loan']['term_months'], int)
    
    # Test string fields
    assert isinstance(contract['contract_type'], str)
    assert isinstance(contract['contract_date'], str)
    
    # Test list fields
    assert isinstance(contract['clients'], list)
    assert isinstance(contract['investors'], list)
    assert isinstance(contract['witnesses'], list)
    assert isinstance(contract['notary'], list)
    assert isinstance(contract['properties'], list)


if __name__ == "__main__":
    # Run tests
    print("Running final contract format tests...")
    
    try:
        test_contract_structure()
        print("✓ Contract structure test passed")
        
        test_person_fields_have_p_prefix()
        print("✓ Person fields p_ prefix test passed")
        
        test_person_role_ids()
        print("✓ Person role IDs test passed")
        
        test_document_structure()
        print("✓ Document structure test passed")
        
        test_address_structure()
        print("✓ Address structure test passed")
        
        test_loan_structure()
        print("✓ Loan structure test passed")
        
        test_property_structure()
        print("✓ Property structure test passed")
        
        test_company_structure()
        print("✓ Company structure test passed")
        
        test_paragraph_request_structure()
        print("✓ Paragraph request structure test passed")
        
        test_data_types()
        print("✓ Data types test passed")
        
        print("\n🎉 All tests passed! The final contract format is valid.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
