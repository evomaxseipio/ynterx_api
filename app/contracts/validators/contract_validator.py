from typing import Dict, Any, List
from fastapi import HTTPException


class ContractValidator:
    """Validador de contratos"""
    
    @staticmethod
    def validate_contract_data(data: Dict[str, Any]) -> List[str]:
        """Validar datos básicos del contrato"""
        errors = []
        
        # Validar campos requeridos
        if not data.get("contract_type"):
            errors.append("contract_type es requerido")
        
        if not data.get("contract_number"):
            errors.append("contract_number es requerido")
        
        # Validar participantes mínimos
        if not data.get("clients") and not data.get("investors"):
            errors.append("Se requiere al menos un cliente o inversionista")
        
        # Validar préstamo si es tipo hipoteca
        if data.get("contract_type") == "mortgage":
            if not data.get("loan"):
                errors.append("Los contratos hipotecarios requieren información de préstamo")
            else:
                loan = data["loan"]
                if not loan.get("amount"):
                    errors.append("El monto del préstamo es requerido")
                if not loan.get("interest_rate"):
                    errors.append("La tasa de interés es requerida")
        
        # Validar propiedades si es tipo hipoteca
        if data.get("contract_type") == "mortgage":
            if not data.get("properties"):
                errors.append("Los contratos hipotecarios requieren al menos una propiedad")
        
        return errors
    
    @staticmethod
    def validate_participants(data: Dict[str, Any]) -> List[str]:
        """Validar participantes del contrato"""
        errors = []
        
        # Validar clientes
        if "clients" in data and data["clients"]:
            for i, client in enumerate(data["clients"]):
                client_errors = ContractValidator._validate_person(client, f"cliente {i+1}")
                errors.extend(client_errors)
        
        # Validar inversionistas
        if "investors" in data and data["investors"]:
            for i, investor in enumerate(data["investors"]):
                investor_errors = ContractValidator._validate_person(investor, f"inversionista {i+1}")
                errors.extend(investor_errors)
        
        # Validar testigos
        if "witnesses" in data and data["witnesses"]:
            for i, witness in enumerate(data["witnesses"]):
                witness_errors = ContractValidator._validate_person(witness, f"testigo {i+1}")
                errors.extend(witness_errors)
        
        # Validar notarios
        notaries = data.get("notaries") or data.get("notary") or []
        if notaries:
            for i, notary in enumerate(notaries):
                notary_errors = ContractValidator._validate_notary(notary, f"notario {i+1}")
                errors.extend(notary_errors)
        
        return errors
    
    @staticmethod
    def _validate_person(person_data: Dict[str, Any], person_type: str) -> List[str]:
        """Validar datos de una persona"""
        errors = []
        
        person = person_data.get("person", {})
        
        # Validar campos requeridos
        if not person.get("p_first_name"):
            errors.append(f"Nombre es requerido para {person_type}")
        
        if not person.get("p_last_name"):
            errors.append(f"Apellido es requerido para {person_type}")
        
        # Validar documentos
        documents = person.get("p_documents", [])
        if not documents:
            errors.append(f"Documento de identidad es requerido para {person_type}")
        else:
            document = documents[0]
            if not document.get("document_number"):
                errors.append(f"Número de documento es requerido para {person_type}")
        
        # Validar direcciones
        addresses = person.get("p_addresses", [])
        if not addresses:
            errors.append(f"Dirección es requerida para {person_type}")
        else:
            address = addresses[0]
            if not address.get("address_line1"):
                errors.append(f"Dirección principal es requerida para {person_type}")
        
        return errors
    
    @staticmethod
    def _validate_notary(notary_data: Dict[str, Any], notary_type: str) -> List[str]:
        """Validar datos de un notario (incluye validación de persona + campos específicos)"""
        errors = []
        
        # Validar datos básicos de persona
        person_errors = ContractValidator._validate_person(notary_data, notary_type)
        errors.extend(person_errors)
        
        person = notary_data.get("person", {})
        additional_data = person.get("p_additional_data", {})
        
        # Validar campos específicos del notario
        if not additional_data.get("license_number"):
            errors.append(f"Número de matrícula (license_number) es requerido para {notary_type}")
        
        if not additional_data.get("office_name"):
            errors.append(f"Nombre de oficina (office_name) es requerido para {notary_type}")
        
        if not additional_data.get("jurisdiction"):
            errors.append(f"Jurisdicción es requerida para {notary_type}")
        
        # Validar que tenga al menos email o teléfono profesional
        professional_email = additional_data.get("professional_email", "")
        professional_phone = additional_data.get("professional_phone", "")
        
        if not professional_email and not professional_phone:
            errors.append(f"Email profesional o teléfono profesional es requerido para {notary_type}")
        
        return errors
    
    @staticmethod
    def validate_loan_data(loan_data: Dict[str, Any]) -> List[str]:
        """Validar datos del préstamo"""
        errors = []
        
        if not loan_data.get("amount"):
            errors.append("El monto del préstamo es requerido")
        elif loan_data["amount"] <= 0:
            errors.append("El monto del préstamo debe ser mayor a 0")
        
        if not loan_data.get("interest_rate"):
            errors.append("La tasa de interés es requerida")
        elif loan_data["interest_rate"] <= 0:
            errors.append("La tasa de interés debe ser mayor a 0")
        
        if not loan_data.get("term_months"):
            errors.append("El plazo del préstamo es requerido")
        elif loan_data["term_months"] <= 0:
            errors.append("El plazo del préstamo debe ser mayor a 0")
        
        return errors
    
    @staticmethod
    def validate_property_data(properties_data: List[Dict[str, Any]]) -> List[str]:
        """Validar datos de propiedades"""
        errors = []
        
        if not properties_data:
            errors.append("Al menos una propiedad es requerida")
            return errors
        
        for i, property_data in enumerate(properties_data):
            if not property_data.get("property_type"):
                errors.append(f"Tipo de propiedad es requerido para propiedad {i+1}")
            
            if not property_data.get("address_line1"):
                errors.append(f"Dirección es requerida para propiedad {i+1}")
            
            if not property_data.get("property_value"):
                errors.append(f"Valor de la propiedad es requerido para propiedad {i+1}")
            elif property_data["property_value"] <= 0:
                errors.append(f"El valor de la propiedad {i+1} debe ser mayor a 0")
        
        return errors
