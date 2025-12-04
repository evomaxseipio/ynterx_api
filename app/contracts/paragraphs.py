# paragraphs.py
import re
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncConnection


async def get_paragraph_from_db(
    connection: AsyncConnection,
    person_role: str,
    contract_type: str,
    section: str,
    contract_services: str = 'mortgage'
) -> Optional[str]:
    """
    Get predefined paragraph from database
    """
    try:
        query = """
            SELECT paragraph_content FROM contract_paragraphs
            WHERE person_role = :person_role
              AND contract_type = :contract_type
              AND section = :section
              AND contract_services = :contract_services
              AND is_active = true
            ORDER BY order_position ASC
            LIMIT 1
        """
        from sqlalchemy import text
        result = await connection.execute(
            text(query),
            {
                "person_role": person_role,
                "contract_type": contract_type,
                "section": section,
                "contract_services": contract_services
            }
        )
        row = result.fetchone()
        print(f"🔍 Obteniendo párrafo de DB: {section} (role: {person_role}, type: {contract_type}, service: {contract_services})")
        if row:
            return row[0]
        return None
    except Exception as e:
        error_str = str(e).lower()
        if "transaction is aborted" in error_str or "infailedsqltransaction" in error_str:
            print(f"⚠️ Transacción abortada al obtener párrafo de DB: {section}")
            return None
        else:
            print(f"Error getting paragraph from DB: {e}")
            return None


def _is_empty_or_default(value: str) -> bool:
    """
    Verifica si un valor está vacío o es un valor por defecto que debe ser omitido
    
    Args:
        value: Valor a verificar
        
    Returns:
        True si el valor está vacío o es un valor por defecto
    """
    if not value:
        return True
    
    value_str = str(value).strip().lower()
    
    # Valores por defecto que deben ser omitidos
    default_values = [
        "xxxxxx@xmail.com",
        "(xxx) xxx-xxxx",
        "[email]",
        "[phone]",
        "[client_email]",
        "[client_phone]",
        "[investor_email]",
        "[investor_phone]",
        "[witness_email]",
        "[witness_phone]",
        "[notary_email]",
        "[notary_phone]"
    ]
    
    return value_str in default_values


def process_paragraph(paragraph_template: str, data: Dict[str, Any]) -> str:
    """
    Process paragraph template by replacing variables with data from JSON
    Elimina las partes del texto que contienen variables vacías o con valores por defecto

    Args:
        paragraph_template: Template with variables {{variable_name}}
        data: Flattened contract data

    Returns:
        Processed paragraph with variables replaced and empty/default sections removed
    """
    if not paragraph_template:
        return ""

    try:
        variables_curly = re.findall(r'\{\{(\w+)\}\}', paragraph_template)
        variables_brackets = re.findall(r'\[(\w+)\]', paragraph_template)
        variables = list(set(variables_curly + variables_brackets))

        processed_paragraph = paragraph_template

        # Primero, eliminar las partes del texto que contienen variables vacías o por defecto
        # Especialmente para teléfono y correo electrónico
        for variable in variables:
            value = data.get(variable, "")
            
            if value is not None:
                value_str = str(value).strip()
            else:
                value_str = ""
            
            # Si el valor está vacío o es un valor por defecto, eliminar la sección correspondiente
            if _is_empty_or_default(value_str):
                # Patrones para eliminar: ", teléfono {{variable}}" o "teléfono {{variable}},"
                # También manejar "correo electrónico {{variable}}"
                patterns_to_remove = [
                    # Patrón: ", teléfono {{variable}}"
                    rf',\s*teléfono\s*{{{{?{re.escape(variable)}}}?}}',
                    # Patrón: "teléfono {{variable}},"
                    rf'teléfono\s*{{{{?{re.escape(variable)}}}?}}\s*,',
                    # Patrón: ", correo electrónico {{variable}}"
                    rf',\s*correo\s+electrónico\s*{{{{?{re.escape(variable)}}}?}}',
                    # Patrón: "correo electrónico {{variable}},"
                    rf'correo\s+electrónico\s*{{{{?{re.escape(variable)}}}?}}\s*,',
                    # Patrón: ", correo electrónico {{variable}}, quien" (al final antes de "quien")
                    rf',\s*correo\s+electrónico\s*{{{{?{re.escape(variable)}}}?}}\s*,?\s*(?=quien)',
                ]
                
                for pattern in patterns_to_remove:
                    processed_paragraph = re.sub(pattern, '', processed_paragraph, flags=re.IGNORECASE)
                
                # También eliminar si está al inicio de una frase: "teléfono {{variable}}"
                processed_paragraph = re.sub(
                    rf'^\s*teléfono\s*{{{{?{re.escape(variable)}}}?}}\s*,?\s*',
                    '',
                    processed_paragraph,
                    flags=re.IGNORECASE | re.MULTILINE
                )
                processed_paragraph = re.sub(
                    rf'^\s*correo\s+electrónico\s*{{{{?{re.escape(variable)}}}?}}\s*,?\s*',
                    '',
                    processed_paragraph,
                    flags=re.IGNORECASE | re.MULTILINE
                )

        # Luego, reemplazar las variables restantes con sus valores
        for variable in variables:
            value = data.get(variable, f"[{variable}]")

            if value is not None:
                value_str = str(value).strip()
            else:
                value_str = f"[{variable}]"

            # Solo reemplazar si el valor no está vacío y no es un valor por defecto
            if not _is_empty_or_default(value_str):
                processed_paragraph = processed_paragraph.replace(
                    f"{{{{{variable}}}}}",
                    value_str
                )
                
                processed_paragraph = processed_paragraph.replace(
                    f"[{variable}]",
                    value_str
                )
            else:
                # Si está vacío o es por defecto, reemplazar con string vacío
                processed_paragraph = processed_paragraph.replace(
                    f"{{{{{variable}}}}}",
                    ""
                )
                
                processed_paragraph = processed_paragraph.replace(
                    f"[{variable}]",
                    ""
                )

        # Limpiar espacios dobles y comas múltiples que puedan quedar
        processed_paragraph = re.sub(r'\s+', ' ', processed_paragraph)  # Múltiples espacios a uno
        processed_paragraph = re.sub(r',\s*,+', ',', processed_paragraph)  # Múltiples comas a una
        processed_paragraph = re.sub(r',\s*,', ',', processed_paragraph)  # Coma seguida de coma
        processed_paragraph = re.sub(r'\s*,\s*,', ',', processed_paragraph)  # Espacios y comas múltiples
        processed_paragraph = processed_paragraph.strip()

        return processed_paragraph

    except Exception as e:
        print(f"Error processing paragraph: {e}")
        return paragraph_template


def _process_multiple_clients_paragraph(paragraph_template: str, data: Dict[str, Any], clients_count: int) -> str:
    """
    Process paragraph for multiple clients in a single consecutive paragraph
    Handles both individual client templates and married couple templates
    
    Args:
        paragraph_template: Paragraph template with generic variables
        data: Flattened contract data with numbered variables
        clients_count: Number of clients
        
    Returns:
        Processed paragraph with all clients in a single paragraph
    """
    if not paragraph_template or clients_count <= 1:
        return process_paragraph(paragraph_template, data)
    
    try:
        actual_clients_count = clients_count
        if actual_clients_count == 0:
            idx = 1
            while f"client{idx}_full_name" in data:
                idx += 1
            actual_clients_count = idx - 1
        
        if actual_clients_count <= 1:
            return process_paragraph(paragraph_template, data)
        
        template_str = paragraph_template.strip()
        
        # Detectar si es un template para casados (contiene "los señores" o variables combinadas)
        is_married_template = (
            "los señores" in template_str.lower() or 
            "los señor" in template_str.lower() or
            "teléfonos" in template_str.lower() or
            "correos electrónicos" in template_str.lower() or
            "y {{client" in template_str.lower()
        )
        
        if is_married_template:
            # Procesar template para casados - combinar ambos clientes en una sola frase
            return _process_married_clients_paragraph(template_str, data, actual_clients_count)
        
        # Template normal - procesar cada cliente por separado
        # Extract parts based on known template structure
        # Template: "De la otra parte, el señor(a) {...}, quien en lo que sigue..."
        initial_prefix_match = re.match(r'^([^,]+,\s*)', template_str, re.IGNORECASE)
        initial_prefix = initial_prefix_match.group(1) if initial_prefix_match else "De la otra parte, "
        
        # Find the final part starting with ", quien en lo que sigue"
        final_part_match = re.search(r',\s*quien en lo que sigue[^.]*\.', template_str, re.IGNORECASE)
        if not final_part_match:
            final_part_match = re.search(r',\s*quien se denominará[^.]*\.', template_str, re.IGNORECASE)
        
        final_part = final_part_match.group(0) if final_part_match else ", quien en lo que sigue del presente acto se denominará LA SEGUNDA PARTE o POR SU PROPIO NOMBRE."
        
        # Extract descriptive part (between prefix and final part)
        descriptive_start = len(initial_prefix)
        descriptive_end = final_part_match.start() if final_part_match else len(template_str)
        descriptive_part = template_str[descriptive_start:descriptive_end].strip()
        
        # Extract client prefix from template (e.g., "el señor(a)")
        client_prefix_match = re.match(r'^(el señor\(a\)|el señor|la señora)\s+', descriptive_part, re.IGNORECASE)
        client_prefix = client_prefix_match.group(1) if client_prefix_match else "el señor(a)"
        
        # Remove client prefix from descriptive part
        descriptive_part_clean = re.sub(r'^(el señor\(a\)|el señor|la señora)\s+', '', descriptive_part, flags=re.IGNORECASE)
        descriptive_part_clean = descriptive_part_clean.strip()
        
        variable_mapping = {
            'client_full_name': 'client{num}_full_name',
            'client_document_number': 'client{num}_document_number',
            'client_nationality': 'client{num}_nationality',
            'client_marital_status': 'client{num}_marital_status',
            'client_address': 'client{num}_address',
            'client_address2': 'client{num}_address2',
            'client_phone': 'client{num}_phone',
            'client_email': 'client{num}_email',
        }
        
        client_parts = []
        for idx in range(1, actual_clients_count + 1):
            client_template = descriptive_part_clean
            for generic_var, numbered_pattern in variable_mapping.items():
                numbered_var = numbered_pattern.format(num=idx)
                client_template = client_template.replace(f"{{{{{generic_var}}}}}", f"{{{{{numbered_var}}}}}")
            
            client_paragraph = process_paragraph(client_template, data).rstrip('.,;').strip()
            
            if idx == 1:
                client_parts.append(f"{initial_prefix}{client_prefix} {client_paragraph}; y")
            elif idx == actual_clients_count:
                final_part_plural = final_part.replace("quien en lo que sigue", "quienes en lo que sigue")
                final_part_plural = final_part_plural.replace("quien se denominará", "quienes se denominarán")
                client_parts.append(f" {client_prefix} {client_paragraph}{final_part_plural}")
            else:
                client_parts.append(f" {client_prefix} {client_paragraph}; y")
        
        return " ".join(client_parts)
        
    except Exception as e:
        print(f"Error processing multiple clients paragraph: {e}")
        return process_paragraph(paragraph_template, data)


def _process_married_clients_paragraph(template_str: str, data: Dict[str, Any], clients_count: int) -> str:
    """
    Process paragraph template for married clients (combined format)
    Combines both clients' information in a single paragraph
    
    Args:
        template_str: Template string with combined variables
        data: Flattened contract data with numbered variables
        clients_count: Number of clients (should be 2 for married couples)
        
    Returns:
        Processed paragraph with combined client information
    """
    try:
        # Obtener datos de ambos clientes
        client1_name = data.get('client1_full_name', '')
        client2_name = data.get('client2_full_name', '')
        client1_doc = data.get('client1_document_number', '')
        client2_doc = data.get('client2_document_number', '')
        client1_nationality = data.get('client1_nationality', '')
        client2_nationality = data.get('client2_nationality', '')
        client1_address = data.get('client1_address', '')
        client2_address = data.get('client2_address', '')
        client1_address2 = data.get('client1_address2', '')
        client2_address2 = data.get('client2_address2', '')
        
        # Obtener teléfonos y correos
        client1_phone = data.get('client1_phone', '') or ''
        client2_phone = data.get('client2_phone', '') or ''
        client1_email = data.get('client1_email', '') or ''
        client2_email = data.get('client2_email', '') or ''
        
        # Filtrar valores vacíos o por defecto
        phones = []
        if not _is_empty_or_default(client1_phone):
            phones.append(client1_phone)
        if not _is_empty_or_default(client2_phone):
            phones.append(client2_phone)
        
        emails = []
        if not _is_empty_or_default(client1_email):
            emails.append(client1_email)
        if not _is_empty_or_default(client2_email):
            emails.append(client2_email)
        
        # Construir texto combinado para nombres
        combined_names = f"{client1_name} y {client2_name}"
        
        # Construir texto combinado para documentos
        combined_docs = f"{client1_doc} y {client2_doc}"
        
        # Construir texto combinado para teléfonos (solo si hay al menos uno)
        phones_text = ""
        if phones:
            if len(phones) == 1:
                phones_text = phones[0]
            else:
                phones_text = " y ".join(phones)
        
        # Construir texto combinado para correos (solo si hay al menos uno)
        emails_text = ""
        if emails:
            if len(emails) == 1:
                emails_text = emails[0]
            else:
                emails_text = " y ".join(emails)
        
        # Construir texto combinado para direcciones
        # Si las direcciones son iguales, mostrar solo una; si son diferentes, mostrar ambas
        addresses_text = ""
        if client1_address and client2_address:
            # Comparar direcciones normalizadas (sin espacios extra, en mayúsculas)
            addr1_norm = client1_address.strip().upper()
            addr2_norm = client2_address.strip().upper()
            if addr1_norm == addr2_norm:
                addresses_text = client1_address
            else:
                # Si son diferentes, mostrar ambas
                addresses_text = f"{client1_address} y {client2_address}"
        elif client1_address:
            addresses_text = client1_address
        elif client2_address:
            addresses_text = client2_address
        
        # Reemplazar variables en el template
        processed = template_str
        
        # Reemplazar nombres - primero las variables numeradas individuales, luego las combinadas
        processed = re.sub(r'\{\{client1_full_name\}\}', client1_name, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client2_full_name\}\}', client2_name, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client_full_name\}\}', combined_names, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client_full_name\]', combined_names, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client1_full_name\]', client1_name, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client2_full_name\]', client2_name, processed, flags=re.IGNORECASE)
        
        # Reemplazar documentos - primero las variables numeradas individuales, luego las combinadas
        processed = re.sub(r'\{\{client1_document_number\}\}', client1_doc, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client2_document_number\}\}', client2_doc, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client_document_number\}\}', combined_docs, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client_document_number\]', combined_docs, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client1_document_number\]', client1_doc, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client2_document_number\]', client2_doc, processed, flags=re.IGNORECASE)
        
        # Reemplazar nacionalidad (asumir que ambos tienen la misma)
        nationality = client1_nationality or client2_nationality
        processed = re.sub(r'\{\{client1_nationality\}\}', nationality, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client2_nationality\}\}', nationality, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client_nationality\}\}', nationality, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client_nationality\]', nationality, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client1_nationality\]', nationality, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client2_nationality\]', nationality, processed, flags=re.IGNORECASE)
        
        # Reemplazar direcciones (también manejar variables individuales)
        processed = re.sub(r'\{\{client1_address\}\}', client1_address or '', processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client2_address\}\}', client2_address or '', processed, flags=re.IGNORECASE)
        processed = re.sub(r'\{\{client_address\}\}', addresses_text, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client_address\]', addresses_text, processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client1_address\]', client1_address or '', processed, flags=re.IGNORECASE)
        processed = re.sub(r'\[client2_address\]', client2_address or '', processed, flags=re.IGNORECASE)
        
        # Manejar teléfonos - PRIMERO reemplazar patrones completos, LUEGO variables individuales
        if phones_text:
            # PRIMERO: Reemplazar patrones completos con variables (antes de reemplazar variables individuales)
            processed = re.sub(
                r'teléfonos\s+\{\{client_phone\}\}\s+y\s+\{\{client2_phone\}\}',
                f'teléfonos {phones_text}',
                processed,
                flags=re.IGNORECASE
            )
            processed = re.sub(
                r'teléfonos\s+\{\{client1_phone\}\}\s+y\s+\{\{client2_phone\}\}',
                f'teléfonos {phones_text}',
                processed,
                flags=re.IGNORECASE
            )
            # LUEGO: Reemplazar variables individuales que queden
            if not _is_empty_or_default(client1_phone):
                processed = re.sub(r'\{\{client1_phone\}\}', client1_phone, processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client1_phone\]', client1_phone, processed, flags=re.IGNORECASE)
            else:
                processed = re.sub(r'\{\{client1_phone\}\}', '', processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client1_phone\]', '', processed, flags=re.IGNORECASE)
            
            if not _is_empty_or_default(client2_phone):
                processed = re.sub(r'\{\{client2_phone\}\}', client2_phone, processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client2_phone\]', client2_phone, processed, flags=re.IGNORECASE)
            else:
                processed = re.sub(r'\{\{client2_phone\}\}', '', processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client2_phone\]', '', processed, flags=re.IGNORECASE)
            
            # Limpiar patrones donde quedó "teléfonos X y " después del reemplazo
            processed = re.sub(
                r'teléfonos\s+([^,]+)\s+y\s+,',
                f'teléfonos \\1',
                processed,
                flags=re.IGNORECASE
            )
            # Reemplazar variable genérica si existe
            processed = re.sub(r'\{\{client_phone\}\}', phones_text, processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client_phone\]', phones_text, processed, flags=re.IGNORECASE)
        else:
            # Eliminar toda la frase de teléfonos si no hay ninguno
            # Primero eliminar patrones con variables
            processed = re.sub(r',\s*teléfonos\s+\{\{client1_phone\}\}\s+y\s+\{\{client2_phone\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'teléfonos\s+\{\{client1_phone\}\}\s+y\s+\{\{client2_phone\}\},?\s*', '', processed, flags=re.IGNORECASE)
            # Luego eliminar cualquier patrón restante
            processed = re.sub(r',\s*teléfonos\s+[^,]+', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'teléfonos\s+[^,]+,\s*', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'teléfonos\s+[^,]+', '', processed, flags=re.IGNORECASE)
            # Reemplazar variables individuales con vacío
            processed = re.sub(r'\{\{client1_phone\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\{\{client2_phone\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client1_phone\]', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client2_phone\]', '', processed, flags=re.IGNORECASE)
        
        # Manejar correos - PRIMERO reemplazar patrones completos, LUEGO variables individuales
        if emails_text:
            # PRIMERO: Reemplazar patrones completos con variables (antes de reemplazar variables individuales)
            processed = re.sub(
                r'correos\s+electrónicos\s+\{\{client_email\}\}\s+y\s+\{\{client2_email\}\}',
                f'correos electrónicos {emails_text}',
                processed,
                flags=re.IGNORECASE
            )
            processed = re.sub(
                r'correos\s+electrónicos\s+\{\{client1_email\}\}\s+y\s+\{\{client2_email\}\}',
                f'correos electrónicos {emails_text}',
                processed,
                flags=re.IGNORECASE
            )
            # LUEGO: Reemplazar variables individuales que queden
            if not _is_empty_or_default(client1_email):
                processed = re.sub(r'\{\{client1_email\}\}', client1_email, processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client1_email\]', client1_email, processed, flags=re.IGNORECASE)
            else:
                processed = re.sub(r'\{\{client1_email\}\}', '', processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client1_email\]', '', processed, flags=re.IGNORECASE)
            
            if not _is_empty_or_default(client2_email):
                processed = re.sub(r'\{\{client2_email\}\}', client2_email, processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client2_email\]', client2_email, processed, flags=re.IGNORECASE)
            else:
                processed = re.sub(r'\{\{client2_email\}\}', '', processed, flags=re.IGNORECASE)
                processed = re.sub(r'\[client2_email\]', '', processed, flags=re.IGNORECASE)
            
            # Limpiar patrones donde quedó "correos electrónicos X y " después del reemplazo
            processed = re.sub(
                r'correos\s+electrónicos\s+([^,]+)\s+y\s+,',
                f'correos electrónicos \\1',
                processed,
                flags=re.IGNORECASE
            )
            # Reemplazar variable genérica si existe
            processed = re.sub(r'\{\{client_email\}\}', emails_text, processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client_email\]', emails_text, processed, flags=re.IGNORECASE)
        else:
            # Eliminar toda la frase de correos si no hay ninguno
            # Primero eliminar patrones con variables
            processed = re.sub(r',\s*correos\s+electrónicos\s+\{\{client1_email\}\}\s+y\s+\{\{client2_email\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'correos\s+electrónicos\s+\{\{client1_email\}\}\s+y\s+\{\{client2_email\}\},?\s*', '', processed, flags=re.IGNORECASE)
            # Luego eliminar cualquier patrón restante
            processed = re.sub(r',\s*correos\s+electrónicos\s+[^,]+', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'correos\s+electrónicos\s+[^,]+,?\s*', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'correos\s+electrónicos\s+[^,]+', '', processed, flags=re.IGNORECASE)
            # Reemplazar variables individuales con vacío
            processed = re.sub(r'\{\{client1_email\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\{\{client2_email\}\}', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client1_email\]', '', processed, flags=re.IGNORECASE)
            processed = re.sub(r'\[client2_email\]', '', processed, flags=re.IGNORECASE)
        
        # Limpiar patrones problemáticos antes de limpiar espacios
        # Eliminar " y ," o " y " seguido de nada (valores vacíos)
        # Patrón: "X y ," -> "X" (cuando el segundo valor está vacío)
        processed = re.sub(r'([^\s,]+)\s+y\s+,', r'\1', processed)  # "X y ," -> "X"
        processed = re.sub(r'\s+y\s+,', '', processed)  # " y ," -> ""
        processed = re.sub(r'\s+y\s+$', '', processed, flags=re.MULTILINE)  # " y " al final -> ""
        
        # Limpiar específicamente patrones en teléfonos y correos
        # "teléfonos X y ," -> "teléfonos X"
        processed = re.sub(r'(teléfonos\s+[^,]+)\s+y\s+,', r'\1', processed, flags=re.IGNORECASE)
        # "correos electrónicos X y ," -> "correos electrónicos X"
        processed = re.sub(r'(correos\s+electrónicos\s+[^,]+)\s+y\s+,', r'\1', processed, flags=re.IGNORECASE)
        
        # Eliminar frases completas de teléfonos/correos si quedaron vacías después del reemplazo
        processed = re.sub(r',\s*teléfonos\s+y\s*,', '', processed, flags=re.IGNORECASE)
        processed = re.sub(r'teléfonos\s+y\s*,', '', processed, flags=re.IGNORECASE)
        processed = re.sub(r',\s*teléfonos\s+$', '', processed, flags=re.IGNORECASE | re.MULTILINE)
        processed = re.sub(r'teléfonos\s+$', '', processed, flags=re.IGNORECASE | re.MULTILINE)
        
        processed = re.sub(r',\s*correos\s+electrónicos\s+y\s*,', '', processed, flags=re.IGNORECASE)
        processed = re.sub(r'correos\s+electrónicos\s+y\s*,', '', processed, flags=re.IGNORECASE)
        processed = re.sub(r',\s*correos\s+electrónicos\s+$', '', processed, flags=re.IGNORECASE | re.MULTILINE)
        processed = re.sub(r'correos\s+electrónicos\s+$', '', processed, flags=re.IGNORECASE | re.MULTILINE)
        
        # Asegurar que haya una coma entre teléfonos y correos electrónicos si ambos están presentes
        # Patrón: "teléfonos X correos" -> "teléfonos X, correos"
        processed = re.sub(
            r'(teléfonos\s+[^,]+)\s+(correos\s+electrónicos)',
            r'\1, \2',
            processed,
            flags=re.IGNORECASE
        )
        
        # Asegurar que haya una coma después de correos electrónicos si hay algo después
        # Patrón: "correos electrónicos X ambos" -> "correos electrónicos X, ambos"
        processed = re.sub(
            r'(correos\s+electrónicos\s+[^,]+)\s+(ambos\s+con|quienes|quien)',
            r'\1, \2',
            processed,
            flags=re.IGNORECASE
        )
        
        # Asegurar que haya una coma después de teléfonos si hay algo después (y no es correos)
        # Patrón: "teléfonos X ambos" -> "teléfonos X, ambos"
        if "correos electrónicos" not in processed.lower():
            processed = re.sub(
                r'(teléfonos\s+[^,]+)\s+(ambos|quienes|quien|domicilio)',
                r'\1, \2',
                processed,
                flags=re.IGNORECASE
            )
        
        # Limpiar espacios y comas múltiples
        processed = re.sub(r'\s+', ' ', processed)
        processed = re.sub(r',\s*,+', ',', processed)
        processed = re.sub(r',\s*,', ',', processed)
        processed = re.sub(r'\s*,\s*,', ',', processed)
        
        # Limpiar comas al inicio o final de frases
        processed = re.sub(r'^,\s+', '', processed)
        processed = re.sub(r'\s+,$', '', processed)
        
        processed = processed.strip()
        
        return processed
        
    except Exception as e:
        print(f"Error processing married clients paragraph: {e}")
        import traceback
        traceback.print_exc()
        return process_paragraph(template_str, data)


async def get_all_paragraphs_for_contract(
    connection: AsyncConnection,
    person_role: str,
    contract_type: str,
    contract_services: str,
    data: Dict[str, Any]
) -> Dict[str, str]:
    """
    Get and process all paragraphs for a contract type and person role
    """
    section_mapping = {
        'identification': 'client_paragraph' if person_role == 'client' else 'investor_paragraph',
        'investors': 'investor_paragraph',
        'clients': 'client_paragraph',
        'witnesses': 'witness_paragraph',
        'notaries': 'notary_paragraph',
        'guarantees': 'guarantee_paragraph',
        'terms_conditions': 'terms_paragraph',
        'payment_terms': 'payment_paragraph',
        'legal_clauses': 'legal_paragraph',
        'signatures': 'signature_paragraph'
    }
    processed_paragraphs = {}
    for db_section, word_variable in section_mapping.items():
        try:
            print(f"🔍 Procesando sección: {db_section} -> Variable de Word: {word_variable}")
            paragraph_template = await get_paragraph_from_db(
                connection,
                person_role=person_role,
                contract_type=contract_type,
                section=db_section,
                contract_services=contract_services
            )
            if paragraph_template:
                if word_variable == 'client_paragraph':
                    clients_count = data.get('clients_count', 0)
                    has_multiple_clients = clients_count > 1 or 'client2_full_name' in data
                    
                    if has_multiple_clients:
                        processed_paragraph = _process_multiple_clients_paragraph(paragraph_template, data, clients_count)
                    else:
                        processed_paragraph = process_paragraph(paragraph_template, data)
                else:
                    processed_paragraph = process_paragraph(paragraph_template, data)
                
                processed_paragraphs[word_variable] = processed_paragraph
                print(f"✅ Procesado: {word_variable} (desde sección '{db_section}')")
        except Exception as e:
            print(f"❌ Error processing {db_section} -> {word_variable}: {e}")
            continue
    return processed_paragraphs


async def get_investor_paragraph(
    connection: AsyncConnection,
    contract_type_id: int,
    investor_data: Dict[str, Any]
) -> str:
    """Generate specific paragraph for investor"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "investors"
    )

    if not paragraph_template:
        paragraph_template = """
        **De una parte**, {{investor_full_name}}, portador de la cédula de identidad
        y electoral No. {{investor_document}}, domiciliado en {{investor_address}},
        {{investor_city}}, quien en lo que sigue del presente acto se denominará
        **LA PRIMERA PARTE o EL ACREEDOR**.
        """

    return process_paragraph(paragraph_template, investor_data)


async def get_client_paragraph(
    connection: AsyncConnection,
    contract_type_id: int,
    client_data: Dict[str, Any]
) -> str:
    """Generate specific paragraph for client"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "clients"
    )

    if not paragraph_template:
        paragraph_template = """
        **De la otra parte**, {{client_full_name}}, {{client_nationality}}, mayor de edad,
        {{client_marital_status}}, portador de la cédula de identidad y electoral
        No. {{client_document}}, domiciliado en {{client_address}}, {{client_city}},
        teléfono {{client_phone}}, quien para lo que sigue de este contrato se denominará
        **"LA SEGUNDA PARTE o EL DEUDOR"**.
        """

    return process_paragraph(paragraph_template, client_data)


async def get_witness_paragraph(
    connection: AsyncConnection,
    contract_type_id: int,
    witness_data: Dict[str, Any]
) -> str:
    """Generate specific paragraph for witness"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "witnesses"
    )

    if not paragraph_template:
        paragraph_template = """
        A los fines de dar fuerza probatoria y respaldo a las declaraciones juradas
        contenidas en este contrato, comparece como **TESTIGO** {{witness_full_name}},
        mayor de edad, portador de la cédula de identidad y electoral No. {{witness_document}}.
        """

    return process_paragraph(paragraph_template, witness_data)


async def get_notary_paragraph(
    connection: AsyncConnection,
    contract_type_id: int,
    notary_data: Dict[str, Any]
) -> str:
    """Generate specific paragraph for notary"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "notaries"
    )

    if not paragraph_template:
        paragraph_template = """
        YO, {{notary_full_name}}, NOTARIO PUBLICO, MATRICULA NO. {{notary_number}},
        CERTIFICO Y DOY FE: DE QUE LAS FIRMAS QUE APARECEN MÁS ARRIBA FUERON PUESTAS
        EN MI PRESENCIA, LIBRE Y VOLUNTARIAMENTE.
        """

    return process_paragraph(paragraph_template, notary_data)


CREATE_TABLE_SQL = """
CREATE TABLE contract_paragraphs (
    id SERIAL PRIMARY KEY,
    contract_type_id INTEGER NOT NULL,
    section VARCHAR(100) NOT NULL,
    order_position INTEGER NOT NULL DEFAULT 1,
    title VARCHAR(255),
    content TEXT NOT NULL,
    paragraph_variables JSONB,
    paragraph_description VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Datos de ejemplo para hipotecas
INSERT INTO contract_paragraphs (contract_type_id, section, order_position, title, content, paragraph_description) VALUES
(1, 'investors', 1, 'Párrafo del Inversionista',
'**De una parte**, la sociedad de comercio **GRUPO REYSA, S.R.L.**, organizada de acuerdo con las leyes de la República Dominicana, **RNC No. 1-3225325-6**, RM. 3187SPM, con domicilio social en {{investor_address}}, {{investor_city}}, República Dominicana, debidamente representada en este contrato por su gerente, {{investor_full_name}}, dominicano, mayor de edad, {{investor_marital_status}}, portador de la cédula de identidad y electoral No.{{investor_document}}, domiciliado en {{investor_address}}, {{investor_city}}, República Dominicana, sociedad que en lo que sigue del presente acto se denominará **LA PRIMERA PARTE o LA ACREEDORA**;',
'Párrafo del inversionista para contratos de hipoteca'),

(1, 'clients', 2, 'Párrafo del Cliente',
'**De la otra parte**, el señor **{{client_full_name}}**, {{client_nationality}}, mayor de edad, {{client_marital_status}}, portador de la cédula de identidad y electoral **No.{{client_document}}**, domiciliado y residente en {{client_address}}, en la ciudad de {{client_city}}, República Dominicana, teléfono {{client_phone}}, correo electrónico {{client_email}}, quien para lo que sigue de este contrato se denominará **"LA SEGUNDA PARTE o EL DEUDOR"**;',
'Párrafo del cliente para contratos de hipoteca'),

(1, 'witnesses', 3, 'Párrafo del Testigo',
'**INTERVENCIÓN DE TESTIGO.-** A los fines de dar fuerza probatoria y respaldo a las declaraciones juradas contenidas en este contrato, comparece como **TESTIGO** {{witness_full_name}}, mayor de edad, portador(a) de la cédula de identidad y electoral No. {{witness_document}}, domiciliado(a) en {{witness_address}}, quien declara haber estado presente al momento de la firma del presente contrato.',
'Párrafo del testigo para contratos de hipoteca'),

(1, 'notaries', 4, 'Párrafo del Notario',
'YO, {{notary_full_name}}, NOTARIO PUBLICO DE LOS DEL NUMERO PARA EL MUNICIPIO DE {{notary_city}}, INSCRITO EN EL COLEGIO DOMINICANO DE NOTARIOS INC., MEDIANTE **MATRICULA NO.{{notary_number}}**, CERTIFICO Y DOY FE: DE QUE LAS FIRMAS QUE APARECEN MÁS ARRIBA FUERON PUESTAS EN MI PRESENCIA, LIBRE Y VOLUNTARIAMENTE POR LOS SEÑORES **{{investor_full_name}}** Y **{{client_full_name}}**.',
'Párrafo del notario para contratos de hipoteca');
"""






