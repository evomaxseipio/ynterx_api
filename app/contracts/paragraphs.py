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
    Obtener párrafo predefinido de la base de datos (nueva estructura)
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
<<<<<<< HEAD
        print(f"Error getting paragraph from DB: {e}")
        return None
=======
        # Manejar específicamente errores de transacción abortada
        error_str = str(e).lower()
        if "transaction is aborted" in error_str or "infailedsqltransaction" in error_str:
            print(f"⚠️ Transacción abortada al obtener párrafo de DB: {section}")
            return None
        else:
            print(f"Error getting paragraph from DB: {e}")
            return None
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f


def process_paragraph(paragraph_template: str, data: Dict[str, Any]) -> str:
    """
    Procesar plantilla de párrafo reemplazando variables con datos del JSON

    Args:
        paragraph_template: Plantilla con variables {{variable_name}}
        data: Datos aplanados del contrato

    Returns:
        Párrafo procesado con variables reemplazadas
    """
    if not paragraph_template:
        return ""

    try:
<<<<<<< HEAD
        # Encontrar todas las variables en el template {{variable}}
        variables = re.findall(r'\{\{(\w+)\}\}', paragraph_template)
=======
        # Encontrar todas las variables en el template {{variable}} o [variable]
        variables_curly = re.findall(r'\{\{(\w+)\}\}', paragraph_template)
        variables_brackets = re.findall(r'\[(\w+)\]', paragraph_template)
        variables = list(set(variables_curly + variables_brackets))
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

        processed_paragraph = paragraph_template

        # Reemplazar cada variable con su valor de los datos
        for variable in variables:
            value = data.get(variable, f"[{variable}]")  # Usar [variable] si no se encuentra

            # Convertir a string y limpiar
            if value is not None:
                value_str = str(value).strip()
            else:
                value_str = f"[{variable}]"

<<<<<<< HEAD
            # Reemplazar en el párrafo
=======
            # Reemplazar variables con formato {{variable}}
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
            processed_paragraph = processed_paragraph.replace(
                f"{{{{{variable}}}}}",
                value_str
            )
<<<<<<< HEAD
=======
            
            # Reemplazar variables con formato [variable]
            processed_paragraph = processed_paragraph.replace(
                f"[{variable}]",
                value_str
            )
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f

        return processed_paragraph

    except Exception as e:
        print(f"Error processing paragraph: {e}")
        return paragraph_template


async def get_all_paragraphs_for_contract(
    connection: AsyncConnection,
    person_role: str,
    contract_type: str,
    contract_services: str,
    data: Dict[str, Any]
) -> Dict[str, str]:
    """
    Obtener y procesar todos los párrafos para un tipo de contrato y rol de persona
    """
    section_mapping = {
<<<<<<< HEAD
=======
        'identification': 'client_paragraph' if person_role == 'client' else 'investor_paragraph',
>>>>>>> 8361536d74cf3c0bd77bab62df6e64a88738668f
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
                processed_paragraph = process_paragraph(paragraph_template, data)
                processed_paragraphs[word_variable] = processed_paragraph
                print(f"✅ Procesado: {word_variable} (desde sección '{db_section}')")
        except Exception as e:
            print(f"❌ Error processing {db_section} -> {word_variable}: {e}")
            continue
    return processed_paragraphs


# Funciones específicas para tipos de párrafos comunes

async def get_investor_paragraph(
    connection: AsyncConnection,
    contract_type_id: int,
    investor_data: Dict[str, Any]
) -> str:
    """Generar párrafo específico del inversionista"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "investors"
    )

    if not paragraph_template:
        # Párrafo por defecto si no existe en DB
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
    """Generar párrafo específico del cliente"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "clients"
    )

    if not paragraph_template:
        # Párrafo por defecto si no existe en DB
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
    """Generar párrafo específico del testigo"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "witnesses"
    )

    if not paragraph_template:
        # Párrafo por defecto si no existe en DB
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
    """Generar párrafo específico del notario"""
    paragraph_template = await get_paragraph_from_db(
        connection,
        contract_type_id,
        "notaries"
    )

    if not paragraph_template:
        # Párrafo por defecto si no existe en DB
        paragraph_template = """
        YO, {{notary_full_name}}, NOTARIO PUBLICO, MATRICULA NO. {{notary_number}},
        CERTIFICO Y DOY FE: DE QUE LAS FIRMAS QUE APARECEN MÁS ARRIBA FUERON PUESTAS
        EN MI PRESENCIA, LIBRE Y VOLUNTARIAMENTE.
        """

    return process_paragraph(paragraph_template, notary_data)


# Tabla de base de datos requerida (para referencia)
CREATE_TABLE_SQL = """
-- La tabla ya existe con esta estructura:
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
