"""
Validador de reglas de negocio para contratos
"""
from typing import Dict, Any, List, Tuple

class ContractValidator:
    """Validador de reglas de negocio para contratos"""
    
    @staticmethod
    def validate_contract_participants(contract_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validar que el contrato cumple con las reglas de negocio de participantes
        
        Returns:
            Tuple[is_valid, error_messages]
        """
        errors = []
        
        # Verificar que hay notario (obligatorio)
        if not contract_data.get("notary") and not contract_data.get("notaries"):
            errors.append("Notario es obligatorio en todos los contratos")
        
        # Verificar tipo de cliente y reglas específicas
        client_type = ContractValidator._get_client_type(contract_data)
        
        if client_type == "juridica_soltera":
            # Jurídica soltera requiere testigo obligatorio
            if not contract_data.get("witnesses"):
                errors.append("Persona jurídica soltera requiere testigo obligatorio")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _get_client_type(contract_data: Dict[str, Any]) -> str:
        """Determinar el tipo de cliente basado en los datos del contrato"""
        
        # Si hay client_company, es empresa
        if contract_data.get("client_company"):
            return "empresa"
        
        # Si hay clients, verificar el tipo de persona
        clients = contract_data.get("clients", [])
        if clients:
            client = clients[0]
            person = client.get("person", {})
            
            # Verificar si es jurídica o física
            if "p_person_role_id" in person:
                # Basado en el role_id, determinar si es jurídica
                # Esto dependería de tu lógica de negocio específica
                pass
            
            # Por ahora, usar un campo específico si existe
            if person.get("is_juridical"):
                marital_status = person.get("p_marital_status", "").lower()
                if marital_status == "soltero":
                    return "juridica_soltera"
                else:
                    return "juridica_casada"
            else:
                marital_status = person.get("p_marital_status", "").lower()
                if marital_status == "soltero":
                    return "fisica_soltera"
                else:
                    return "fisica_casada"
        
        return "unknown"
    
    @staticmethod
    def validate_contract_structure(contract_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar estructura básica del contrato"""
        errors = []
        
        required_fields = [
            "contract_type",
            "contract_date",
            "loan",
            "properties"
        ]
        
        for field in required_fields:
            if not contract_data.get(field):
                errors.append(f"Campo '{field}' es obligatorio")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_loan_data(loan_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validar datos del préstamo"""
        errors = []
        
        required_loan_fields = [
            "amount",
            "currency",
            "interest_rate",
            "term_months",
            "loan_type"
        ]
        
        for field in required_loan_fields:
            if not loan_data.get(field):
                errors.append(f"Campo de préstamo '{field}' es obligatorio")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_properties_data(properties_data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validar datos de propiedades"""
        errors = []
        
        if not properties_data:
            errors.append("Al menos una propiedad es obligatoria")
            return False, errors
        
        for i, property_data in enumerate(properties_data):
            required_property_fields = [
                "property_type",
                "cadastral_number",
                "title_number",
                "property_role"
            ]
            
            for field in required_property_fields:
                if not property_data.get(field):
                    errors.append(f"Propiedad {i+1}: campo '{field}' es obligatorio")
        
        return len(errors) == 0, errors

