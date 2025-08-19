"""
Pruebas unitarias para todas las combinaciones de contratos (40 combinaciones)
"""
import pytest
import json
from typing import Dict, Any
from tests.contracts.validators.contract_validator import ContractValidator

class TestContractCombinations:
    """Pruebas para todas las combinaciones posibles de contratos"""
    
    # ============================================================================
    # GRUPO 1: Cliente Persona Física Soltera + Inversionista Persona (4 combinaciones)
    # ============================================================================
    
    def test_combination_1_fisica_soltera_persona_with_witness_referent(self, base_contract_data, person_fisica_soltera, person_fisica_casada, witness_data, referent_data, notary_data):
        """Caso 1: Cliente Física Soltera + Inversionista Persona + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_2_fisica_soltera_persona_with_witness_only(self, base_contract_data, person_fisica_soltera, person_fisica_casada, witness_data, notary_data):
        """Caso 2: Cliente Física Soltera + Inversionista Persona + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_3_fisica_soltera_persona_with_referent_only(self, base_contract_data, person_fisica_soltera, person_fisica_casada, referent_data, notary_data):
        """Caso 3: Cliente Física Soltera + Inversionista Persona + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_4_fisica_soltera_persona_minimal(self, base_contract_data, person_fisica_soltera, person_fisica_casada, notary_data):
        """Caso 4: Cliente Física Soltera + Inversionista Persona + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 2: Cliente Persona Física Soltera + Inversionista Empresa (4 combinaciones)
    # ============================================================================
    
    def test_combination_5_fisica_soltera_company_with_witness_referent(self, base_contract_data, person_fisica_soltera, company_data, witness_data, referent_data, notary_data):
        """Caso 5: Cliente Física Soltera + Inversionista Empresa + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_6_fisica_soltera_company_with_witness_only(self, base_contract_data, person_fisica_soltera, company_data, witness_data, notary_data):
        """Caso 6: Cliente Física Soltera + Inversionista Empresa + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_7_fisica_soltera_company_with_referent_only(self, base_contract_data, person_fisica_soltera, company_data, referent_data, notary_data):
        """Caso 7: Cliente Física Soltera + Inversionista Empresa + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_8_fisica_soltera_company_minimal(self, base_contract_data, person_fisica_soltera, company_data, notary_data):
        """Caso 8: Cliente Física Soltera + Inversionista Empresa + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 3: Cliente Persona Física Casada + Inversionista Persona (4 combinaciones)
    # ============================================================================
    
    def test_combination_9_fisica_casada_persona_with_witness_referent(self, base_contract_data, person_fisica_casada, person_fisica_soltera, witness_data, referent_data, notary_data):
        """Caso 9: Cliente Física Casada + Inversionista Persona + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_10_fisica_casada_persona_with_witness_only(self, base_contract_data, person_fisica_casada, person_fisica_soltera, witness_data, notary_data):
        """Caso 10: Cliente Física Casada + Inversionista Persona + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_11_fisica_casada_persona_with_referent_only(self, base_contract_data, person_fisica_casada, person_fisica_soltera, referent_data, notary_data):
        """Caso 11: Cliente Física Casada + Inversionista Persona + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_12_fisica_casada_persona_minimal(self, base_contract_data, person_fisica_casada, person_fisica_soltera, notary_data):
        """Caso 12: Cliente Física Casada + Inversionista Persona + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 4: Cliente Persona Física Casada + Inversionista Empresa (4 combinaciones)
    # ============================================================================
    
    def test_combination_13_fisica_casada_company_with_witness_referent(self, base_contract_data, person_fisica_casada, company_data, witness_data, referent_data, notary_data):
        """Caso 13: Cliente Física Casada + Inversionista Empresa + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_14_fisica_casada_company_with_witness_only(self, base_contract_data, person_fisica_casada, company_data, witness_data, notary_data):
        """Caso 14: Cliente Física Casada + Inversionista Empresa + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_15_fisica_casada_company_with_referent_only(self, base_contract_data, person_fisica_casada, company_data, referent_data, notary_data):
        """Caso 15: Cliente Física Casada + Inversionista Empresa + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investor_company"] = company_data
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_16_fisica_casada_company_minimal(self, base_contract_data, person_fisica_casada, company_data, notary_data):
        """Caso 16: Cliente Física Casada + Inversionista Empresa + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_fisica_casada]
        contract_data["investor_company"] = company_data
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 5: Cliente Persona Jurídica Soltera + Inversionista Persona (4 combinaciones)
    # ============================================================================
    
    def test_combination_17_juridica_soltera_persona_with_witness_referent(self, base_contract_data, person_juridica_soltera, person_fisica_casada, witness_data, referent_data, notary_data):
        """Caso 17: Cliente Jurídica Soltera + Inversionista Persona + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_18_juridica_soltera_persona_with_witness_only(self, base_contract_data, person_juridica_soltera, person_fisica_casada, witness_data, notary_data):
        """Caso 18: Cliente Jurídica Soltera + Inversionista Persona + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_19_juridica_soltera_persona_with_referent_only_should_fail(self, base_contract_data, person_juridica_soltera, person_fisica_casada, referent_data, notary_data):
        """Caso 19: Cliente Jurídica Soltera + Inversionista Persona + Notario + Referidor (sin testigo) - DEBE FALLAR"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert not is_valid, "Debería fallar porque jurídica soltera requiere testigo"
        assert any("testigo obligatorio" in error for error in errors)
    
    def test_combination_20_juridica_soltera_persona_minimal_should_fail(self, base_contract_data, person_juridica_soltera, person_fisica_casada, notary_data):
        """Caso 20: Cliente Jurídica Soltera + Inversionista Persona + Notario (sin testigo, sin referidor) - DEBE FALLAR"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investors"] = [person_fisica_casada]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert not is_valid, "Debería fallar porque jurídica soltera requiere testigo"
        assert any("testigo obligatorio" in error for error in errors)
    
    # ============================================================================
    # GRUPO 6: Cliente Persona Jurídica Soltera + Inversionista Empresa (4 combinaciones)
    # ============================================================================
    
    def test_combination_21_juridica_soltera_company_with_witness_referent(self, base_contract_data, person_juridica_soltera, company_data, witness_data, referent_data, notary_data):
        """Caso 21: Cliente Jurídica Soltera + Inversionista Empresa + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_22_juridica_soltera_company_with_witness_only(self, base_contract_data, person_juridica_soltera, company_data, witness_data, notary_data):
        """Caso 22: Cliente Jurídica Soltera + Inversionista Empresa + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_23_juridica_soltera_company_with_referent_only_should_fail(self, base_contract_data, person_juridica_soltera, company_data, referent_data, notary_data):
        """Caso 23: Cliente Jurídica Soltera + Inversionista Empresa + Notario + Referidor (sin testigo) - DEBE FALLAR"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert not is_valid, "Debería fallar porque jurídica soltera requiere testigo"
        assert any("testigo obligatorio" in error for error in errors)
    
    def test_combination_24_juridica_soltera_company_minimal_should_fail(self, base_contract_data, person_juridica_soltera, company_data, notary_data):
        """Caso 24: Cliente Jurídica Soltera + Inversionista Empresa + Notario (sin testigo, sin referidor) - DEBE FALLAR"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_soltera]
        contract_data["investor_company"] = company_data
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert not is_valid, "Debería fallar porque jurídica soltera requiere testigo"
        assert any("testigo obligatorio" in error for error in errors)
    
    # ============================================================================
    # GRUPO 7: Cliente Persona Jurídica Casada + Inversionista Persona (4 combinaciones)
    # ============================================================================
    
    def test_combination_25_juridica_casada_persona_with_witness_referent(self, base_contract_data, person_juridica_casada, person_fisica_soltera, witness_data, referent_data, notary_data):
        """Caso 25: Cliente Jurídica Casada + Inversionista Persona + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_26_juridica_casada_persona_with_witness_only(self, base_contract_data, person_juridica_casada, person_fisica_soltera, witness_data, notary_data):
        """Caso 26: Cliente Jurídica Casada + Inversionista Persona + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_27_juridica_casada_persona_with_referent_only(self, base_contract_data, person_juridica_casada, person_fisica_soltera, referent_data, notary_data):
        """Caso 27: Cliente Jurídica Casada + Inversionista Persona + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_28_juridica_casada_persona_minimal(self, base_contract_data, person_juridica_casada, person_fisica_soltera, notary_data):
        """Caso 28: Cliente Jurídica Casada + Inversionista Persona + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 8: Cliente Persona Jurídica Casada + Inversionista Empresa (4 combinaciones)
    # ============================================================================
    
    def test_combination_29_juridica_casada_company_with_witness_referent(self, base_contract_data, person_juridica_casada, company_data, witness_data, referent_data, notary_data):
        """Caso 29: Cliente Jurídica Casada + Inversionista Empresa + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_30_juridica_casada_company_with_witness_only(self, base_contract_data, person_juridica_casada, company_data, witness_data, notary_data):
        """Caso 30: Cliente Jurídica Casada + Inversionista Empresa + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investor_company"] = company_data
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_31_juridica_casada_company_with_referent_only(self, base_contract_data, person_juridica_casada, company_data, referent_data, notary_data):
        """Caso 31: Cliente Jurídica Casada + Inversionista Empresa + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investor_company"] = company_data
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_32_juridica_casada_company_minimal(self, base_contract_data, person_juridica_casada, company_data, notary_data):
        """Caso 32: Cliente Jurídica Casada + Inversionista Empresa + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["clients"] = [person_juridica_casada]
        contract_data["investor_company"] = company_data
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 9: Cliente Empresa + Inversionista Persona (4 combinaciones)
    # ============================================================================
    
    def test_combination_33_company_persona_with_witness_referent(self, base_contract_data, company_data, person_fisica_soltera, witness_data, referent_data, notary_data):
        """Caso 33: Cliente Empresa + Inversionista Persona + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_34_company_persona_with_witness_only(self, base_contract_data, company_data, person_fisica_soltera, witness_data, notary_data):
        """Caso 34: Cliente Empresa + Inversionista Persona + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_35_company_persona_with_referent_only(self, base_contract_data, company_data, person_fisica_soltera, referent_data, notary_data):
        """Caso 35: Cliente Empresa + Inversionista Persona + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_36_company_persona_minimal(self, base_contract_data, company_data, person_fisica_soltera, notary_data):
        """Caso 36: Cliente Empresa + Inversionista Persona + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investors"] = [person_fisica_soltera]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    # ============================================================================
    # GRUPO 10: Cliente Empresa + Inversionista Empresa (4 combinaciones)
    # ============================================================================
    
    def test_combination_37_company_company_with_witness_referent(self, base_contract_data, company_data, witness_data, referent_data, notary_data):
        """Caso 37: Cliente Empresa + Inversionista Empresa + Notario + Testigo + Referidor"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investor_company"] = company_data  # Usar la misma empresa para simplificar
        contract_data["witnesses"] = [witness_data]
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_38_company_company_with_witness_only(self, base_contract_data, company_data, witness_data, notary_data):
        """Caso 38: Cliente Empresa + Inversionista Empresa + Notario + Testigo (sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investor_company"] = company_data  # Usar la misma empresa para simplificar
        contract_data["witnesses"] = [witness_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_39_company_company_with_referent_only(self, base_contract_data, company_data, referent_data, notary_data):
        """Caso 39: Cliente Empresa + Inversionista Empresa + Notario + Referidor (sin testigo)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investor_company"] = company_data  # Usar la misma empresa para simplificar
        contract_data["referents"] = [referent_data]
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"
    
    def test_combination_40_company_company_minimal(self, base_contract_data, company_data, notary_data):
        """Caso 40: Cliente Empresa + Inversionista Empresa + Notario (sin testigo, sin referidor)"""
        contract_data = base_contract_data.copy()
        contract_data["client_company"] = company_data
        contract_data["investor_company"] = company_data  # Usar la misma empresa para simplificar
        contract_data["notary"] = [notary_data]
        
        is_valid, errors = ContractValidator.validate_contract_participants(contract_data)
        assert is_valid, f"Debería ser válido: {errors}"

