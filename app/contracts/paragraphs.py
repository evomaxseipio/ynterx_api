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


def process_paragraph(paragraph_template: str, data: Dict[str, Any]) -> str:
    """
    Process paragraph template by replacing variables with data from JSON

    Args:
        paragraph_template: Template with variables {{variable_name}}
        data: Flattened contract data

    Returns:
        Processed paragraph with variables replaced
    """
    if not paragraph_template:
        return ""

    try:
        variables_curly = re.findall(r'\{\{(\w+)\}\}', paragraph_template)
        variables_brackets = re.findall(r'\[(\w+)\]', paragraph_template)
        variables = list(set(variables_curly + variables_brackets))

        processed_paragraph = paragraph_template

        for variable in variables:
            value = data.get(variable, f"[{variable}]")

            if value is not None:
                value_str = str(value).strip()
            else:
                value_str = f"[{variable}]"

            processed_paragraph = processed_paragraph.replace(
                f"{{{{{variable}}}}}",
                value_str
            )
            
            processed_paragraph = processed_paragraph.replace(
                f"[{variable}]",
                value_str
            )

        return processed_paragraph

    except Exception as e:
        print(f"Error processing paragraph: {e}")
        return paragraph_template


def _process_multiple_clients_paragraph(paragraph_template: str, data: Dict[str, Any], clients_count: int) -> str:
    """
    Process paragraph for multiple clients in a single consecutive paragraph
    
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
        
        start_patterns = [
            r'\*\*De la otra parte\*\*,\s*',
            r'\*\*De la otra parte\*\*\s*',
            r'De la otra parte,\s*',
            r'De la otra parte\s*'
        ]
        
        descriptive_start = 0
        for pattern in start_patterns:
            match = re.search(pattern, template_str, re.IGNORECASE)
            if match:
                descriptive_start = match.end()
                break
        
        end_patterns = [
            r',\s*quien para lo que sigue',
            r',\s*quienes para lo que sigue',
            r',\s*quien se denominará',
            r',\s*quienes se denominarán',
            r'quien para lo que sigue',
            r'quienes para lo que sigue'
        ]
        
        descriptive_end = len(template_str)
        final_part = ""
        for pattern in end_patterns:
            match = re.search(pattern, template_str, re.IGNORECASE)
            if match:
                descriptive_end = match.start()
                final_part = template_str[match.start():].strip()
                break
        
        descriptive_part = template_str[descriptive_start:descriptive_end].strip()
        
        if not descriptive_part:
            descriptive_part = re.sub(r'^\*\*De la otra parte\*\*,\s*', '', template_str, flags=re.IGNORECASE)
            descriptive_part = re.sub(r'^\*\*De la otra parte\*\*\s*', '', descriptive_part, flags=re.IGNORECASE)
            for pattern in end_patterns:
                match = re.search(pattern, descriptive_part, re.IGNORECASE)
                if match:
                    final_part = descriptive_part[match.start():].strip()
                    descriptive_part = descriptive_part[:match.start()].strip()
                    break
        
        if not final_part:
            remaining_part = template_str[descriptive_end:].strip()
            if remaining_part:
                final_part = remaining_part
            else:
                print(f"⚠️ No se encontró parte final en template, usando template completo para último cliente")
                final_part = ""
        
        initial_prefix = ""
        for pattern in start_patterns:
            match = re.search(pattern, template_str, re.IGNORECASE)
            if match:
                initial_prefix = match.group(0).strip()
                break
        
        if not initial_prefix:
            initial_match = re.match(r'^(\*\*[^*]+\*\*[,\s]*)', template_str, re.IGNORECASE)
            if initial_match:
                initial_prefix = initial_match.group(1).strip()
        
        first_client_prefix_match = re.match(r'^(el señor|la señora|el|la)\s+', descriptive_part, re.IGNORECASE)
        first_client_prefix = first_client_prefix_match.group(0) if first_client_prefix_match else ""
        
        def get_client_prefix(client_idx: int) -> str:
            """Get appropriate prefix based on client gender"""
            gender = data.get(f"client{client_idx}_gender", "").lower()
            if gender in ["f", "female", "femenino", "femenina"]:
                return "la señora"
            elif gender in ["m", "male", "masculino", "masculina"]:
                return "el señor"
            return first_client_prefix if first_client_prefix else ""
        
        descriptive_part_clean = re.sub(r'^(el señor|la señora|el|la)\s+', '', descriptive_part, flags=re.IGNORECASE)
        descriptive_part_clean = descriptive_part_clean.strip()
        
        variable_mapping = {
            'client_full_name': 'client{num}_full_name',
            'client_document': 'client{num}_document_number',
            'client_nationality': 'client{num}_nationality',
            'client_marital_status': 'client{num}_marital_status',
            'client_address': 'client{num}_address',
            'client_city': 'client{num}_city',
            'client_phone': 'client{num}_phone',
            'client_email': 'client{num}_email',
        }
        
        client_parts = []
        
        for idx in range(1, actual_clients_count + 1):
            client_num = idx
            client_template = descriptive_part_clean
            
            for generic_var, numbered_pattern in variable_mapping.items():
                numbered_var = numbered_pattern.format(num=client_num)
                client_template = client_template.replace(f"{{{{{generic_var}}}}}", f"{{{{{numbered_var}}}}}")
                client_template = client_template.replace(f"[{generic_var}]", f"[{numbered_var}]")
            
            client_paragraph = process_paragraph(client_template, data)
            client_paragraph = client_paragraph.strip()
            
            if idx == 1:
                client_paragraph = client_paragraph.rstrip('.,;')
                if initial_prefix:
                    if first_client_prefix:
                        full_prefix = f"{initial_prefix} {first_client_prefix}"
                    else:
                        full_prefix = initial_prefix
                else:
                    full_template_first = paragraph_template
                    for generic_var, numbered_pattern in variable_mapping.items():
                        numbered_var = numbered_pattern.format(num=client_num)
                        full_template_first = full_template_first.replace(f"{{{{{generic_var}}}}}", f"{{{{{numbered_var}}}}}")
                        full_template_first = full_template_first.replace(f"[{generic_var}]", f"[{numbered_var}]")
                    processed_first = process_paragraph(full_template_first, data)
                    prefix_match = re.match(r'^(\*\*[^*]+\*\*[,\s]*(?:el señor|la señora|el|la)?\s*)', processed_first, re.IGNORECASE)
                    if prefix_match:
                        full_prefix = prefix_match.group(1).strip()
                        client_paragraph = re.sub(r'^\*\*[^*]+\*\*[,\s]*(?:el señor|la señora|el|la)?\s*', '', processed_first, flags=re.IGNORECASE).strip()
                        client_paragraph = client_paragraph.rstrip('.,;')
                    else:
                        full_prefix = initial_prefix if initial_prefix else ""
                client_paragraph = f"{full_prefix} {client_paragraph}; y" if full_prefix else f"{client_paragraph}; y"
            elif idx == actual_clients_count:
                client_paragraph = client_paragraph.rstrip('.,;')
                client_prefix = get_client_prefix(client_num)
                
                if final_part:
                    prefix_text = f"; y {client_prefix} " if client_prefix else "; y "
                    client_paragraph = f"{prefix_text}{client_paragraph}"
                    final_part_plural = final_part.replace("quien para lo que sigue", "quienes para lo que sigue")
                    final_part_plural = final_part_plural.replace("quien se denominará", "quienes se denominarán")
                    if not final_part_plural.startswith(','):
                        final_part_plural = f", {final_part_plural}"
                    client_paragraph = f"{client_paragraph}{final_part_plural}"
                else:
                    full_template_for_last = paragraph_template
                    for generic_var, numbered_pattern in variable_mapping.items():
                        numbered_var = numbered_pattern.format(num=client_num)
                        full_template_for_last = full_template_for_last.replace(f"{{{{{generic_var}}}}}", f"{{{{{numbered_var}}}}}")
                        full_template_for_last = full_template_for_last.replace(f"[{generic_var}]", f"[{numbered_var}]")
                    
                    last_client_full = process_paragraph(full_template_for_last, data)
                    last_client_full = last_client_full.replace("quien para lo que sigue", "quienes para lo que sigue")
                    last_client_full = last_client_full.replace("quien se denominará", "quienes se denominarán")
                    last_client_clean = re.sub(r'^\*\*[^*]+\*\*[,\s]*', '', last_client_full, flags=re.IGNORECASE)
                    last_client_clean = re.sub(r'^(el señor|la señora|el|la)\s+', '', last_client_clean, flags=re.IGNORECASE)
                    prefix_text = f"; y {client_prefix} " if client_prefix else "; y "
                    client_paragraph = f"{prefix_text}{last_client_clean.strip()}"
            else:
                client_paragraph = client_paragraph.rstrip('.,;')
                client_prefix = get_client_prefix(client_num)
                prefix_text = f"; y {client_prefix} " if client_prefix else "; y "
                client_paragraph = f"{prefix_text}{client_paragraph}; y"
            
            client_parts.append(client_paragraph)
        
        result = " ".join(client_parts)
        return result
        
    except Exception as e:
        print(f"Error processing multiple clients paragraph: {e}")
        return process_paragraph(paragraph_template, data)


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






